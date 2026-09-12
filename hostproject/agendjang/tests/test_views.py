from django.test import TestCase
from django.urls import reverse

from agendjang.models import Task, Tag


class CalendarViewTest(TestCase):
    def test_renders_with_tag_list_in_context(self):
        tag = Tag.objects.create(name="Home")

        response = self.client.get(reverse('agendjang:view_calendar'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agendjang/calendar.html')
        self.assertIn(tag, response.context['tag_list'])

    def test_only_non_done_tasks_of_a_tag_are_listed(self):
        """This is focused on the accordion view only"""
        tag = Tag.objects.create(name="Home")
        todo = Task.objects.create(name="Todo task")
        todo.many_tags.add(tag)
        done = Task.objects.create(name="Done task", done=True)
        done.many_tags.add(tag)

        response = self.client.get(reverse('agendjang:view_calendar'))

        self.assertContains(response, "Todo task")
        self.assertNotContains(response, "Done task")

    def test_archived_tasks_of_a_tag_are_not_listed(self):
        """tag.task_set is built on top of the model's custom manager, so it
        inherits the archive filtering just like Task.objects.all() does."""
        tag = Tag.objects.create(name="Home")
        archived = Task.objects.create(name="Archived task", archive=True)
        archived.many_tags.add(tag)

        response = self.client.get(reverse('agendjang:view_calendar'))

        self.assertNotContains(response, "Archived task")


class JavascriptCalendarViewTest(TestCase):
    def test_renders_as_javascript(self):
        response = self.client.get(reverse('agendjang:view_js_calendar'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/javascript')


class HelpViewTest(TestCase):
    def test_renders_markdown_help_file_as_html(self):
        response = self.client.get(reverse('agendjang:help'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<h1>Task manipulation</h1>", response.content)


class TaskCreateUpdateViewTest(TestCase):
    def test_get_create_form(self):
        response = self.client.get(reverse('agendjang:create_task'))
        self.assertEqual(response.status_code, 200)

    def test_post_creates_task_and_redirects_to_calendar(self):
        response = self.client.post(
            reverse('agendjang:create_task'),
            data={
                'name': 'New task',
                'points': 3,
            }
        )

        self.assertRedirects(response, reverse('agendjang:view_calendar'))
        self.assertTrue(Task.objects.filter(name='New task', points=3).exists())

    def test_post_invalid_data_does_not_create_task(self):
        response = self.client.post(reverse('agendjang:create_task'), data={'points': 3})

        self.assertEqual(response.status_code, 200)  # re-renders form with errors
        self.assertEqual(Task.objects.count(), 0)

        errors = response.context['form'].errors.as_data()
        self.assertEqual(errors.keys(), {'name'})
        self.assertEqual(errors['name'][0].code, 'required')
        self.assertEqual(errors['name'][0].messages, ['This field is required.'])

    def test_post_updates_existing_task(self):
        task = Task.objects.create(name='Original')

        response = self.client.post(
            reverse('agendjang:update_task', args=[task.pk]),
            data={'name': 'Renamed', 'points': 5, 'done': 'on'},
        )

        self.assertRedirects(response, reverse('agendjang:view_calendar'))
        task.refresh_from_db()
        self.assertEqual(task.name, 'Renamed')
        self.assertEqual(task.points, 5)
        self.assertTrue(task.done)


class TagCreateUpdateViewTest(TestCase):
    def test_post_creates_tag_and_redirects_to_calendar(self):
        response = self.client.post(reverse('agendjang:create_tag'), data={'name': 'Work'})

        self.assertRedirects(response, reverse('agendjang:view_calendar'))
        self.assertTrue(Tag.objects.filter(name='Work').exists())

    def test_post_duplicate_name_does_not_create_tag(self):
        Tag.objects.create(name='Work')

        response = self.client.post(reverse('agendjang:create_tag'), data={'name': 'Work'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Tag.objects.filter(name='Work').count(), 1)

        errors = response.context['form'].errors.as_data()
        self.assertEqual(errors.keys(), {'name'})
        self.assertEqual(errors['name'][0].code, 'unique')
        self.assertEqual(errors['name'][0].messages, ['Tag with this Name already exists.'])

    def test_post_updates_existing_tag(self):
        tag = Tag.objects.create(name='Old name')

        response = self.client.post(
            reverse('agendjang:update_tag', args=[tag.pk]),
            data={'name': 'New name'},
        )

        self.assertRedirects(response, reverse('agendjang:view_calendar'))
        tag.refresh_from_db()
        self.assertEqual(tag.name, 'New name')
