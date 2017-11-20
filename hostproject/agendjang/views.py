from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy

from agendjang.models import Task, DateRange, Tag
from agendjang.forms import TaskForm
from agendjang.serializers import TaskSerializer, DateRangeSerializer

from rest_framework import viewsets


#######
# API #
#######

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()  # don't like, could be taken from name or serializer todo mixin
    serializer_class = TaskSerializer


class DateRangeViewSet(viewsets.ModelViewSet):
    queryset = DateRange.objects.all()
    serializer_class = DateRangeSerializer


#############
# Templates #
#############

class TaskCreate(CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('view_calendar')


class TaskUpdate(UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('view_calendar')


class TaskList(ListView):
    model = Task


class TaskDetail(DetailView):
    model = Task


class TagList(ListView):
    model = Tag


class CalendarView(TemplateView):
    template_name = 'agendjang/calendar.html'


class JavascriptCalendarView(ListView):
    model = Task  # listview because i export tasklist in the js calendar as django tags
    template_name = 'agendjang/js_calendar.js'
