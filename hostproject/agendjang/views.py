from django.shortcuts import HttpResponse
from django.template import loader
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.utils import timezone
from django.urls import reverse_lazy

from agendjang.models import Task, ScheduledTask, DateRange, Tag
from agendjang.forms import TaskForm, ScheduledTaskForm, TagForm
from agendjang.serializers import TaskSerializer, DateRangeSerializer, EventSerializer

from rest_framework import viewsets
from rest_framework.response import Response

from markdown import markdown

from datetime import timedelta


#######
# API #
#######


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class DateRangeViewSet(viewsets.ModelViewSet):
    queryset = DateRange.objects.all()
    serializer_class = DateRangeSerializer


class EventViewSet(viewsets.ViewSet):
    def list(self, request):

        start = self.request.query_params.get('start')  # not tz aware, by vary from date to datetime
        end = self.request.query_params.get('end')

        qs = []

        for task in Task.objects.all():
            for daterange in task.daterange_set.filter(start_date__gte=start, end_date__lte=end):
                qs.append({
                    'task_id': task.id,
                    'id': daterange.pk,
                    'title': task.name,
                    'start': daterange.start_date,
                    'end': daterange.end_date,
                    'allDay': True if daterange.end_date - daterange.start_date == timedelta(hours=24) else False,
                    'color': 'red' if (not task.done and timezone.now() > daterange.end_date) else 'green',
                })

        serializer = EventSerializer(qs, many=True)
        return Response(serializer.data)


#############
# Templates #
#############

def help_view(request):
    """read a markdown help file and convert it to html"""
    return HttpResponse(markdown(loader.render_to_string('agendjang/help.md')))


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


class ScheduledTaskCreate(CreateView):
    model = ScheduledTask
    form_class = ScheduledTaskForm
    success_url = reverse_lazy('view_calendar')


class ScheduledTaskUpdate(UpdateView):
    model = ScheduledTask
    form_class = ScheduledTaskForm
    success_url = reverse_lazy('view_calendar')


class TagCreate(CreateView):
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy('view_calendar')


class TagUpdate(UpdateView):
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy('view_calendar')


class CalendarView(TemplateView):
    template_name = 'agendjang/calendar.html'

    def get_context_data(self, **kwargs):  # adds the tag_list template tag, along object_list
        ctx = super().get_context_data(**kwargs)
        ctx['tag_list'] = Tag.objects.all()
        ctx['schedtask_list'] = ScheduledTask.objects.all()
        return ctx


class JavascriptCalendarView(ListView):
    model = Task  # listview because i export tasklist in the js calendar as django tags
    template_name = 'agendjang/js_calendar.js'
    content_type = 'text/javascript'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tag_list'] = Tag.objects.all()
        return ctx
