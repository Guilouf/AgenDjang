from django.contrib import admin

from agendjang import models

admin.site.register(models.Task)
admin.site.register(models.ScheduledTask)
admin.site.register(models.Tag)
admin.site.register(models.DateRange)
