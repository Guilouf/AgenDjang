from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from agendjang.models import Task, DateRange, Tag


class TaskModelTest(TestCase):
    def test_defaults(self):
        task = Task.objects.create(name="Do dishes")
        self.assertFalse(task.done)
        self.assertFalse(task.archive)
        self.assertEqual(task.points, 1)
        self.assertEqual(task.description, '')

    def test_str(self):
        task = Task.objects.create(name="Do dishes")
        self.assertEqual(str(task), "Task Do dishes")

    def test_manager_all_excludes_archived_tasks(self):
        active = Task.objects.create(name="Active")
        Task.objects.create(name="Archived", archive=True)

        self.assertEqual(list(Task.objects.all()), [active])

    def test_manager_filter_is_not_restricted_to_active_tasks(self):
        """TaskManager only overrides all(), so an explicit filter() still
        reaches archived tasks. This documents current behaviour: only
        code paths that call .all() get the archive filtering for free."""
        archived = Task.objects.create(name="Archived", archive=True)

        self.assertEqual(list(Task.objects.filter(archive=True)), [archived])

    def test_zero_points_is_valid(self):
        task = Task(name="Task", points=0)
        task.full_clean()  # should not raise

    def test_negative_points_is_invalid(self):
        task = Task(name="Task", points=-1)
        with self.assertRaises(ValidationError):
            task.full_clean()


class DateRangeModelTest(TestCase):
    def setUp(self):
        self.task = Task.objects.create(name="Task")
        self.start = timezone.make_aware(timezone.datetime(2024, 1, 1, 10, 0))
        self.end = timezone.make_aware(timezone.datetime(2024, 1, 1, 12, 0))

    def test_str(self):
        dr = DateRange.objects.create(start_date=self.start, end_date=self.end, task=self.task)
        self.assertEqual(str(dr), f"DateRange {self.start}")

    def test_add_shifts_both_dates_without_mutating_original(self):
        # fixme test dead code
        dr = DateRange(start_date=self.start, end_date=self.end, task=self.task)
        shifted = dr + timedelta(days=1)

        self.assertEqual(shifted.start_date, self.start + timedelta(days=1))
        self.assertEqual(shifted.end_date, self.end + timedelta(days=1))
        # original untouched
        self.assertEqual(dr.start_date, self.start)
        self.assertEqual(dr.end_date, self.end)
        # __add__ builds a brand new, unsaved instance
        self.assertIsNone(shifted.pk)

    def test_deleted_when_task_is_deleted(self):
        dr = DateRange.objects.create(start_date=self.start, end_date=self.end, task=self.task)
        self.task.delete()
        self.assertFalse(DateRange.objects.filter(pk=dr.pk).exists())


class TagModelTest(TestCase):
    def test_str(self):
        tag = Tag.objects.create(name="Work")
        self.assertEqual(str(tag), "Tag Work")

    def test_name_must_be_unique(self):
        Tag.objects.create(name="Work")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Tag.objects.create(name="Work")
