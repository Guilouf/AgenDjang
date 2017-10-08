from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from agendjang.models import Task


class TaskList(ListView):
    model = Task
