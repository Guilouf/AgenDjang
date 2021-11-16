from django.urls import path, include
from agendjang import views
from rest_framework import routers


# For DRF:
router = routers.DefaultRouter()
# no regex here
router.register(r'tasks', views.TaskViewSet, basename='tasks')  # basename for reverse url tags
router.register(r'dateranges', views.DateRangeViewSet, basename='dateranges')
router.register(r'events', views.EventViewSet, basename='events')

urlpatterns = [
    # api root path
    path('api/', include((router.urls, 'api')), ),  # optional url namespace

    # Other urls
    path('help', views.help_view, name='help'),

    # calendars
    path('', views.CalendarView.as_view(), name='view_calendar'),
    path('js_calendar', views.JavascriptCalendarView.as_view(), name='view_js_calendar'),

    # Tasks
    path('create_task', views.TaskCreate.as_view(), name='create_task'),
    path('update_task/<int:pk>', views.TaskUpdate.as_view(), name='update_task'),
    path('tasks', views.TaskList.as_view(), name='list_task'),
    path('tasks/<int:pk>', views.TaskDetail.as_view(), name='detail_task'),

    # ScheduledTasks
    path('create_schedtask', views.ScheduledTaskCreate.as_view(), name='create_schedtask'),
    path('update_schedtask/<int:pk>', views.ScheduledTaskUpdate.as_view(), name='update_schedtask'),

    # Tags
    path('create_tag', views.TagCreate.as_view(), name='create_tag'),
    path('update_tag/<int:pk>', views.TagUpdate.as_view(), name='update_tag'),

]
