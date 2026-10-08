from django import forms
from agendjang.models import Task, Tag


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            # matches the model's MinValueValidator(0): gives a client-side hint too,
            # even though the server-side validator is what actually enforces it
            'points': forms.NumberInput(attrs={'min': 0}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'


class TaskCreateForm(TaskForm):
    """Task form that also schedules the new task, on the calendar day it was created from"""
    start_date = forms.DateTimeField(widget=forms.HiddenInput)
    end_date = forms.DateTimeField(widget=forms.HiddenInput)
