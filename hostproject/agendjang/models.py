from django.db import models


class Task(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    many_tags = models.ManyToManyField('Tag', blank=True)
    done_date = models.DateTimeField(null=True, blank=True)
    points = models.IntegerField(default=1)


    # done = models.BooleanField(default=False)  # fixme par rapport aux répétitions..?? plutot integer ?
    # date_range = models.DurationField()  # use with datetime.timedelta
    # chronicity = models.DurationField(null=True, blank=True)  # how often is it repeated
    # repeats = models.IntegerField(null=True, blank=True)  # how many times its repeated (null never, 0 infinite)


# class Schedule(models.Model):
#     pass


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
