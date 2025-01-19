from rest_framework import serializers

from subnet_api_server.subnets.models import TaskRecord


class TaskRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskRecord
        fields = "__all__"
