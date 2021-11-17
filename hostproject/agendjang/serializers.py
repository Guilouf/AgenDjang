from rest_framework import serializers
from agendjang.models import Task, DateRange


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class DateRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DateRange
        fields = '__all__'


class EventSerializer(serializers.Serializer):
    """Serializer for calendar events displayed in fullcalendar"""
    task_id = serializers.IntegerField()
    title = serializers.CharField()

    id = serializers.IntegerField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

    allDay = serializers.BooleanField()
    color = serializers.CharField()
