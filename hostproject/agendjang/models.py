from django.db import models


class Task(models.Model):
    """
    Procrastinated task
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False)
    points = models.IntegerField(default=1)
    # color = models.Col  # django-colorfield pe

    many_tags = models.ManyToManyField('Tag', blank=True)
    many_dateranges = models.ManyToManyField('DateRange', blank=True)

    # todo add subtasks ?

    def __str__(self):
        return f"Task {self.name}"


class ScheduledTask(Task):
    """
    Instanciate new tasks, with its task attributes
    """
    CHRON_CHOICE = [('days', 'Day'), ('weeks', 'Week'), ('months', 'Month'), ('years', 'Year')]
    chronicity = models.CharField(choices=CHRON_CHOICE, max_length=50)
    # non required because dateranges are not required in Tasks

    repeats = models.PositiveIntegerField()  # how many times its repeated (0 infinite)
    # keep a trace of all instantiated tasks
    many_tasks = models.ManyToManyField('Task', null=True, blank=True, related_name="linked_tasks")


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
