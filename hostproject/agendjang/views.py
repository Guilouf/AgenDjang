from pathlib import Path

from django.http import HttpResponse
from django.views.generic import TemplateView, CreateView, UpdateView
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
        start = request.query_params.get('start')
        end = request.query_params.get('end')

        # parse the first part of the string, containing only the date (ignore time string)
        start = timezone.make_aware(datetime.strptime(start[0:10], '%Y-%m-%d'))
        end = timezone.make_aware(datetime.strptime(end[0:10], '%Y-%m-%d'))

        # overlap, not containment: a daterange that only partially overlaps the
        # requested window must still be returned (the calendar widget clips it itself)
        dateranges = DateRange.objects.select_related('task').filter(
            task__archive=False,  # excludes archived tasks, in a single query
            start_date__lt=end,
            end_date__gt=start,
        )

        qs = [
            {
                'taskId': daterange.task_id,
                'id': daterange.pk,
                'title': daterange.task.name,
                'start': daterange.start_date,
                'end': daterange.end_date,
                'allDay': daterange.end_date - daterange.start_date == timedelta(hours=24),
                'color': 'red' if (not daterange.task.done and timezone.now() > daterange.end_date) else 'green',
            }
            for daterange in dateranges
        ]

        serializer = EventSerializer(qs, many=True)
        return Response(serializer.data)


#############
# Templates #
#############

def help_view(request):
    """Read a markdown help file and convert it to html."""
    help_md_path = Path(__file__).resolve().parent / 'templates' / 'agendjang' / 'help.md'
    return HttpResponse(markdown(help_md_path.read_text()))


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


class JavascriptCalendarView(TemplateView):
    template_name = 'agendjang/js_calendar.js'
    content_type = 'text/javascript'
