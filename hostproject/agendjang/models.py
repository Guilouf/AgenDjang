from django.db import models


class TaskManager(models.Manager):
    """Overrides the default manager all() method in order to only return results that are not archived"""

    def all(self):
        return self.filter(archive=False)


class Task(models.Model):
    """
    Procrastinated task
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    points = models.IntegerField(default=1)
    # color = models.Col  # django-colorfield pe

    many_tags = models.ManyToManyField('Tag', blank=True)
    many_dateranges = models.ManyToManyField('DateRange', blank=True)

    objects = TaskManager()

    # todo add subtasks ?

    def __str__(self):
        return f"Task {self.name}"


class ScheduledTask(Task):
    """
    Instanciate new tasks, with its task attributes
    """

    # keep a trace of all instantiated tasks
    many_tasks = models.ManyToManyField('Task', blank=True, related_name="linked_tasks")


class DateRange(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"DateRange, {self.start_date}"

    def __add__(self, other):
        return DateRange(start_date=self.start_date + other, end_date=self.end_date + other)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        return self  # allow to chain the save method


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    # color =

    def __str__(self):
        return f"Tag {self.name}"
