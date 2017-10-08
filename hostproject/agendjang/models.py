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

    # todo des subtasks ?

    def __str__(self):
        return f"Task {self.name}"


class ScheduledTask(Task):
    """
    Inherit from Task, or add in task attributes as non required fields ?
    """
    many_tags = models.ManyToManyField('Tag', blank=True)  # todo add default tags (daily, monthly, onetime..)
    failed = models.BooleanField(default=False)  # if task not done before the deadline
    # fixme a task can't be both failed and done. rather have to be infered, or add unicity constraint ?
    # deadline = models.DateTimeField()
    # chronicity = models.DurationField(null=True, blank=True)  # how often is it repeated
    # repeats = models.IntegerField(null=True, blank=True)  # how many times its repeated (null never, 0 infinite)


class DateRange(models.Model):
    start_date = models.DateTimeField()
    range = models.DurationField()  # use with datetime.timedelta
    # fixme start date+range or start + end date ?

    def __str__(self):
        return f"DateRange, {self.start_date}"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    # color =

    def __str__(self):
        return f"Tag {self.name}"
