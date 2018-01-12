from django import forms
from agendjang.models import Task, Tag


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        exclude = ['done_date']


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
