from django import forms
from django.db.models import Q
from agendjang.models import Task, Tag, Project


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            # matches the model's MinValueValidator(0): gives a client-side hint too,
            # even though the server-side validator is what actually enforces it
            'points': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # done projects are hidden, except the task's own, so that editing a task of a done project stays valid
        self.fields['project'].queryset = Project.objects.filter(Q(done=False) | Q(pk=self.instance.project_id))


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectCreateForm(forms.ModelForm):
    """Project form without done: a new project has no tasks to be done yet"""
    class Meta:
        model = Project
        fields = ['name', 'description']


class TaskCreateForm(TaskForm):
    """Task form that also schedules the new task, on the calendar day it was created from"""
    start_date = forms.DateTimeField(widget=forms.HiddenInput)
    end_date = forms.DateTimeField(widget=forms.HiddenInput)
