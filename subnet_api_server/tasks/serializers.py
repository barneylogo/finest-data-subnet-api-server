from rest_framework import serializers

from subnet_api_server.subnets.models import Neuron, TaskRecord


class NeuronSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neuron
        fields = "__all__"

class TaskRecordSerializer(serializers.ModelSerializer):
    neuron = NeuronSerializer(read_only=True)

    class Meta:
        model = TaskRecord
        fields = "__all__"
