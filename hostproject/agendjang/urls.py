from django.urls import path, include
from agendjang import views
from rest_framework import routers


# For DRF:
router = routers.DefaultRouter()
# no regex here
router.register(r'tasks', views.TaskViewSet, basename='tasks')  # basename for reverse url tags
router.register(r'dateranges', views.DateRangeViewSet, basename='dateranges')
router.register(r'events', views.EventViewSet, basename='events')

# https://docs.djangoproject.com/en/3.2/intro/tutorial03/#namespacing-url-names
app_name = 'agendjang'  # all urls here will have this namespace

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

    # Tags
    path('create_tag', views.TagCreate.as_view(), name='create_tag'),
    path('update_tag/<int:pk>', views.TagUpdate.as_view(), name='update_tag'),

]
