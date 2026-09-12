from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from agendjang.models import Task, DateRange


class TaskApiTest(APITestCase):
    def test_list_excludes_archived_tasks(self):
        active = Task.objects.create(name="Active")
        Task.objects.create(name="Archived", archive=True)

        response = self.client.get(reverse('agendjang:api:tasks-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [t['id'] for t in response.data]
        self.assertEqual(ids, [active.id])

    def test_retrieve_archived_task_is_not_found(self):
        """The viewset's queryset is Task.objects.all(), which is already
        filtered by the custom manager, so this applies to every action,
        not just list()."""
        archived = Task.objects.create(name="Archived", archive=True)

        response = self.client.get(reverse('agendjang:api:tasks-detail', args=[archived.pk]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_task(self):
        response = self.client.post(reverse('agendjang:api:tasks-list'), data={
            'name': 'New task',
            'points': 2,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Task.objects.filter(name='New task', points=2).exists())

    def test_delete_task(self):
        task = Task.objects.create(name="To delete")

        response = self.client.delete(reverse('agendjang:api:tasks-detail', args=[task.pk]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())


class DateRangeApiTest(APITestCase):
    def setUp(self):
        self.task = Task.objects.create(name="Task")
        self.start = timezone.now()
        self.end = self.start + timedelta(hours=2)

    def test_create_daterange_linked_to_task(self):
        response = self.client.post(reverse('agendjang:api:dateranges-list'), data={
            'start_date': self.start.isoformat(),
            'end_date': self.end.isoformat(),
            'task': self.task.pk,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DateRange.objects.filter(task=self.task).exists())

    def test_cannot_link_daterange_to_archived_task(self):
        """Archived tasks are excluded from the task manager's default
        queryset, which DRF uses to validate the 'task' relation, so the
        archived task id is rejected as if it didn't exist."""
        archived_task = Task.objects.create(name="Archived", archive=True)

        response = self.client.post(reverse('agendjang:api:dateranges-list'), data={
            'start_date': self.start.isoformat(),
            'end_date': self.end.isoformat(),
            'task': archived_task.pk,
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('task', response.data)

    def test_delete_daterange_does_not_delete_task(self):
        dr = DateRange.objects.create(start_date=self.start, end_date=self.end, task=self.task)

        response = self.client.delete(reverse('agendjang:api:dateranges-detail', args=[dr.pk]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())


class EventApiTest(APITestCase):
    def setUp(self):
        self.today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    def get_events(self, start=None, end=None):
        query_start = (self.today - timedelta(days=10)).strftime('%Y-%m-%d')
        query_end = (self.today + timedelta(days=10)).strftime('%Y-%m-%d')

        return self.client.get(reverse('agendjang:api:events-list'), {
            'start': start or query_start,
            'end': end or query_end,
        })

    def test_overdue_undone_task_is_red(self):
        task = Task.objects.create(name="Overdue", done=False)
        DateRange.objects.create(
            start_date=self.today - timedelta(days=3),
            end_date=self.today - timedelta(days=2),
            task=task,
        )

        response = self.get_events()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['color'], 'red')

    def test_overdue_done_task_is_green(self):
        task = Task.objects.create(name="Overdue but done", done=True)
        DateRange.objects.create(
            start_date=self.today - timedelta(days=3),
            end_date=self.today - timedelta(days=2),
            task=task,
        )

        response = self.get_events()

        self.assertEqual(response.data[0]['color'], 'green')

    def test_future_undone_task_is_green(self):
        task = Task.objects.create(name="Future", done=False)
        DateRange.objects.create(
            start_date=self.today + timedelta(days=2),
            end_date=self.today + timedelta(days=3),
            task=task,
        )

        response = self.get_events()

        self.assertEqual(response.data[0]['color'], 'green')

    def test_all_day_event_flagged_when_exactly_24_hours(self):
        task = Task.objects.create(name="All day")
        DateRange.objects.create(
            start_date=self.today + timedelta(days=1),
            end_date=self.today + timedelta(days=2),
            task=task,
        )

        response = self.get_events()

        self.assertTrue(response.data[0]['allDay'])

    def test_non_24_hour_event_is_not_flagged_all_day(self):
        task = Task.objects.create(name="Short meeting")
        DateRange.objects.create(
            start_date=self.today + timedelta(days=1, hours=9),
            end_date=self.today + timedelta(days=1, hours=11),
            task=task,
        )

        response = self.get_events()

        self.assertFalse(response.data[0]['allDay'])

    def test_dateranges_outside_the_requested_window_are_excluded(self):
        task = Task.objects.create(name="Way in the future")
        DateRange.objects.create(
            start_date=self.today + timedelta(days=20),
            end_date=self.today + timedelta(days=21),
            task=task,
        )

        response = self.get_events()

        self.assertEqual(response.data, [])

    def test_dateranges_of_archived_tasks_are_excluded(self):
        task = Task.objects.create(name="Archived", archive=True)
        DateRange.objects.create(
            start_date=self.today,
            end_date=self.today + timedelta(days=1),
            task=task,
        )

        response = self.get_events()

        self.assertEqual(response.data, [])

    def test_daterange_overlapping_the_window_edge_is_still_included(self):
        """A daterange that starts before the requested window but ends inside
        it (or vice-versa) overlaps the window and must be returned, even
        though it isn't fully contained within [start, end]."""
        task = Task.objects.create(name="Straddles window start")
        DateRange.objects.create(
            start_date=self.today - timedelta(days=15),  # starts well before the window
            end_date=self.today - timedelta(days=9),  # ends inside the window (window starts at -10)
            task=task,
        )

        response = self.get_events()

        self.assertEqual(len(response.data), 1)

    def test_only_the_date_part_of_start_and_end_params_is_used(self):
        """Week/day views send full datetimes; the view should truncate
        them to the date part instead of erroring out."""
        task = Task.objects.create(name="Task")
        DateRange.objects.create(
            start_date=self.today,
            end_date=self.today + timedelta(days=1),
            task=task,
        )

        response = self.get_events(
            start=self.today.strftime('%Y-%m-%dT00:00:00'),
            end=(self.today + timedelta(days=1)).strftime('%Y-%m-%dT23:59:59'),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
