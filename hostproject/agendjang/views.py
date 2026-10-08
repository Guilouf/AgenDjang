from pathlib import Path

from django.db import transaction
from django.http import HttpResponse
from django.views.generic import TemplateView, CreateView, UpdateView
from django.utils import timezone
from django.urls import reverse_lazy

from agendjang.models import Task, DateRange, Tag
from agendjang.forms import TaskForm, TaskCreateForm, TagForm
from agendjang.serializers import DateRangeSerializer, EventSerializer

from rest_framework import viewsets
from rest_framework.response import Response

from markdown import markdown

from datetime import timedelta, datetime


#######
# API #
#######


class DateRangeViewSet(viewsets.ModelViewSet):
    queryset = DateRange.objects.all()
    serializer_class = DateRangeSerializer


class EventViewSet(viewsets.ViewSet):
    def list(self, request):
        """'start' and 'end' params are ISO datetimes with the browser's UTC offset"""
        start = datetime.fromisoformat(request.query_params.get('start'))
        end = datetime.fromisoformat(request.query_params.get('end'))

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
                # known limitation (won't fix): on DST-change days a local day lasts 23h or 25h,
                # so all-day tasks created on those days show as timed events
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
    form_class = TaskCreateForm
    success_url = reverse_lazy('agendjang:view_calendar')

    def get_initial(self):
        # the calendar passes the clicked day's range as query params
        return self.request.GET.dict()

    def form_valid(self, form):
        # No Task left without its DateRange on this view
        with transaction.atomic():
            response = super().form_valid(form)
            DateRange.objects.create(
                task=self.object,
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
            )
        return response


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


class TagListView(TemplateView):
    """Sidebar of tags and their tasks, reloaded on its own after each form submit"""
    template_name = 'agendjang/_tag_list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tag_list'] = Tag.objects.all()
        return ctx


class CalendarView(TagListView):
    template_name = 'agendjang/calendar.html'
