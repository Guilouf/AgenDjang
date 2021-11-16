from rest_framework.serializers import ModelSerializer
from agendjang.models import Task, DateRange


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class DateRangeSerializer(ModelSerializer):
    class Meta:
        model = DateRange
        fields = '__all__'
