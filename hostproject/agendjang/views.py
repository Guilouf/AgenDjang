from django.shortcuts import HttpResponse
from django.template import loader
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.utils import timezone
from django.urls import reverse_lazy

from agendjang.models import Task, DateRange, Tag
from agendjang.forms import TaskForm, TagForm
from agendjang.serializers import TaskSerializer, DateRangeSerializer, EventSerializer

from rest_framework import viewsets
from rest_framework.response import Response

from markdown import markdown

from datetime import timedelta, datetime


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
        """With calendar month view, 'start' and 'end' params are dates,
         but in week and day views they are datetime.
         We parse only the date part of the date, because reducing results with hour precision is useless"""
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        # parse the first part of the string, containing only the date (ignore time string)
        start = timezone.make_aware(datetime.strptime(start[0:10], '%Y-%m-%d'))
        end = timezone.make_aware(datetime.strptime(end[0:10], '%Y-%m-%d'))

        qs = []

        for task in Task.objects.all():
            for daterange in task.daterange_set.filter(start_date__gte=start, end_date__lte=end):
                qs.append({
                    'taskId': task.id,
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
    """Read a markdown help file and convert it to html"""
    return HttpResponse(markdown(loader.render_to_string('agendjang/help.md')))


class TaskCreate(CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('agendjang:view_calendar')


class TaskUpdate(UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('agendjang:view_calendar')


class TagCreate(CreateView):
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy('agendjang:view_calendar')


class TagUpdate(UpdateView):
    model = Tag
    form_class = TagForm
    success_url = reverse_lazy('agendjang:view_calendar')


class CalendarView(TemplateView):
    template_name = 'agendjang/calendar.html'

    def get_context_data(self, **kwargs):  # adds the tag_list template tag, along object_list
        ctx = super().get_context_data(**kwargs)
        ctx['tag_list'] = Tag.objects.all()
        return ctx


class JavascriptCalendarView(ListView):
    model = Task  # ListView because i export TaskList in the js calendar as django tags
    template_name = 'agendjang/js_calendar.js'
    content_type = 'text/javascript'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tag_list'] = Tag.objects.all()
        return ctx
