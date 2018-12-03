from django import forms
from django.core.exceptions import ValidationError
from agendjang.models import Task, ScheduledTask, Tag
from django.db import transaction

from dateutil.relativedelta import relativedelta


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'


class ScheduledTaskForm(forms.ModelForm):
    CHRON_CHOICE = [('days', 'Day'), ('weeks', 'Week'), ('months', 'Month'), ('years', 'Year')]
    chronicity = forms.ChoiceField(choices=CHRON_CHOICE)
    repeats = forms.IntegerField(min_value=0, initial=0)  # how many times its repeated (0 infinite)

    class Meta:
        model = ScheduledTask
        fields = '__all__'

    def clean(self):
        """
        Instantiate the tasks based on the scheduled task
        """
        with transaction.atomic():
            if self.cleaned_data['repeats'] != 0:  # finite number of repetitions
                self.cleaned_data['many_tasks'] = list(self.cleaned_data['many_tasks'])

                try:
                    task_name = self.instance.many_tasks.last().name
                    # by instance ok because by definition always in update, ValueError in case of create
                    index = int(task_name.split('_')[-1])  # get the task "number"
                except (AttributeError, ValueError):  # there's no similar existing task
                    index = 1

                for i in range(index, self.cleaned_data['repeats']+index):
                    task = Task.objects.create(name=f"{self.cleaned_data['name']}_{i+1}",  # first 1 = linked with schedtask
                                               description=self.cleaned_data['description'],
                                               points=self.cleaned_data['points'])
                    task.many_tags.set(list(self.cleaned_data['many_tags']))

                    self.cleaned_data['many_tasks'].append(task)

                    if self.cleaned_data['many_dateranges'].exists():  # checks if the inherited task has a daterange
                        chron = {self.cleaned_data['chronicity']: i}  # kwargs for relativedelta
                        # then copy and add a timedelta to these dateranges for the new task (cf Dateranges __add__)
                        task.many_dateranges.set([(daterange + relativedelta(**chron)).save()  # no full_clean, should be ok
                                                  for daterange in self.cleaned_data['many_dateranges']])
                    else:
                        raise ValidationError({'many_dateranges': 'Scheduled Tasks needs at least one DateRange'})

        else:  # infinite repetitions
            pass  # gros bordel


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
