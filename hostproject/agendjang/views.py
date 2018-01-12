from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from django.urls import reverse_lazy

from agendjang.models import Task, DateRange, Tag
from agendjang.forms import TaskForm, TagForm
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


class TagCreate(CreateView):
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy('view_calendar')


class CalendarView(TemplateView):
    template_name = 'agendjang/calendar.html'

    def get_context_data(self, **kwargs):  # adds the tag_list template tag, along object_list
        ctx = super(CalendarView, self).get_context_data(**kwargs)
        ctx['tag_list'] = Tag.objects.all()
        return ctx


class JavascriptCalendarView(ListView):
    model = Task  # listview because i export tasklist in the js calendar as django tags
    # todo faudrait pouvoir donner une liste de models.. faire une mixin bien classe...
    template_name = 'agendjang/js_calendar.js'

    def get_context_data(self, **kwargs):
        ctx = super(JavascriptCalendarView, self).get_context_data(**kwargs)
        ctx['tag_list'] = Tag.objects.all()
        return ctx
