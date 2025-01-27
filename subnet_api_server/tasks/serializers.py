from rest_framework import serializers
from subnet_api_server.subnets.models import Neuron, ScoreRecord, TaskRecord, WarcFile


class WarcFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarcFile
        fields = "__all__"


class ScoreRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreRecord
        fields = "__all__"


class NeuronSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neuron
        fields = "__all__"


class TaskRecordResponseSerializer(serializers.ModelSerializer):
    miner = NeuronSerializer(read_only=True)
    warc_files = WarcFileSerializer(many=True, read_only=True)

    class Meta:
        model = TaskRecord
        fields = "__all__"


class ScoresResponseSerializer(serializers.ModelSerializer):
    validator = NeuronSerializer(read_only=True)

    class Meta:
        model = ScoreRecord
        fields = ["validator", "score", "created_at"]


class TaskRecordRequestSerializer(serializers.Serializer):
    count = serializers.IntegerField(required=False)
