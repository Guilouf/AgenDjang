from django.conf.urls import url, include
from agendjang import views


urlpatterns = [
    # calendar
    url(r'^calendar$', views.CalendarView.as_view(), name='view_calendar'),

    # Tasks
    url(r'^create_task$', views.TaskCreate.as_view(), name='create_task'),
    url(r'^tasks$', views.TaskList.as_view(), name='list_task'),
    url(r'^tasks/(?P<pk>\d+)$', views.TaskDetail.as_view(), name='detail_task'),
]
