from rest_framework import serializers

from subnet_api_server.subnets.models import Neuron, TaskRecord, WarcFile

class WarcFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarcFile
        fields = "__all__"


class NeuronSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neuron
        fields = "__all__"

class TaskRecordSerializer(serializers.ModelSerializer):
    neuron = NeuronSerializer(read_only=True)
    warc_files = WarcFileSerializer(many=True, read_only=True)

    class Meta:
        model = TaskRecord
        fields = "__all__"
