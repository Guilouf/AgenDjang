from django.conf.urls import url, include
from agendjang import views


urlpatterns = [
    url(r'^tasks$', views.TaskList.as_view(), name='task_list'),
]
