from pathlib import Path

from django.db import transaction
from django.db.models import Prefetch, Max, Count, F
from django.http import HttpResponse
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.utils import timezone
from django.urls import reverse_lazy

from agendjang.models import Task, DateRange, Tag, Project
from agendjang.forms import TaskForm, TaskCreateForm, TagForm, ProjectForm, ProjectCreateForm
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


class ProjectCreate(CreateView):
    model = Project
    form_class = ProjectCreateForm
    success_url = reverse_lazy('agendjang:view_calendar')


class ProjectUpdate(UpdateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('agendjang:view_calendar')


class TagListView(ListView):
    """Sidebar of tags and their tasks, reloaded on its own after each form submit"""
    model = Tag
    template_name = 'agendjang/_tag_list.html'


class ProjectListView(ListView):
    """Sidebar of projects and their tasks, reloaded on its own after each form submit"""
    # to_attr since TaskManager.all() filters, so project.task_set.all would query again, unordered
    queryset = Project.objects.prefetch_related(Prefetch(
        'task_set',
        queryset=Task.objects.filter(archive=False).order_by('-done', 'pk'),
        to_attr='sorted_tasks',
    )).order_by('-done', 'pk')
    template_name = 'agendjang/_project_list.html'

    def get_queryset(self):
        # done projects only with the sidebar's "Show completed projects" checkbox
        queryset = super().get_queryset()
        if self.request.GET.get('show_done'):
            return queryset
        return queryset.filter(done=False)


class CalendarView(TemplateView):
    template_name = 'agendjang/calendar.html'


class StatsView(TemplateView):
    """Done tasks per tag between the 'start' and 'end' params, the period shown by the calendar"""
    template_name = 'agendjang/_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start = datetime.fromisoformat(self.request.GET['start'])
        end = datetime.fromisoformat(self.request.GET['end'])

        # no completion date in the model: a task is considered done at the start of its last daterange.
        # Its start rather than its end, since an all-day task on the period's last day ends exactly at 'end'
        done_tasks = Task.objects.filter(archive=False, done=True).annotate(
            done_date=Max('daterange__start_date'),
        ).filter(done_date__gte=start, done_date__lt=end)

        # grouped on the task side: the m2m is left joined, so tasks without tags come out as a tag None row.
        # done_tasks as a subquery, since it's already grouped by task for its Max
        context['tag_counts'] = Task.objects.filter(pk__in=done_tasks.values('pk')).values(
            tag=F('many_tags__name'),
        ).annotate(done_count=Count('pk')).order_by('-done_count', 'tag')

        context['start'] = start
        context['last_day'] = end - timedelta(days=1)
        return context
