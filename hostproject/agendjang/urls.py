from django.conf.urls import url, include
from agendjang import views
from rest_framework import routers


# For DRF:
router = routers.DefaultRouter()
# no regex here
router.register(r'tasks', views.TaskViewSet, base_name='tasks')  # basename for reverse url tags
router.register(r'dateranges', views.DateRangeViewSet, base_name='dateranges')

urlpatterns = [
    # api root path
    url(r'^api/', include((router.urls, 'api')), ),  # optional url namespace

    # calendars
    url(r'^$', views.CalendarView.as_view(), name='view_calendar'),
    url(r'^js_calendar$', views.JavascriptCalendarView.as_view(), name='view_js_calendar'),

    # Tasks
    url(r'^create_task$', views.TaskCreate.as_view(), name='create_task'),
    url(r'^update_task/(?P<pk>\d+)$', views.TaskUpdate.as_view(), name='update_task'),
    url(r'^tasks$', views.TaskList.as_view(), name='list_task'),
    url(r'^tasks/(?P<pk>\d+)$', views.TaskDetail.as_view(), name='detail_task'),

    # ScheduledTasks
    url(r'^create_schedtask$', views.ScheduledTaskCreate.as_view(), name='create_schedtask'),

    # Tags
    url(r'^create_tag$', views.TagCreate.as_view(), name='create_tag'),
    url(r'^update_tag/(?P<pk>\d+)$', views.TagUpdate.as_view(), name='update_tag'),


]
