from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy

from agendjang.models import Task
from agendjang.forms import TaskForm


class TaskCreate(CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('list_task')


class TaskList(ListView):
    model = Task


class TaskDetail(DetailView):
    model = Task

class CalendarView(TemplateView):
    template_name = 'agendjang/calendar.html'
