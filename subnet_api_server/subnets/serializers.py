from rest_framework import serializers


class CheckTaskRequestSerializer(serializers.Serializer):
    uid = serializers.IntegerField()


class CheckTaskResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    task_id = serializers.IntegerField()
    warc_files = serializers.ListField(child=serializers.CharField())
    request_block = serializers.IntegerField()


class ReportScoreRequestSerializer(serializers.Serializer):
    hotkey = serializers.CharField()
    task_id = serializers.IntegerField()
    score = serializers.FloatField()
    signature = serializers.CharField()


class FinishTaskRequestSerializer(serializers.Serializer):
    hotkey = serializers.CharField()
    hf_repo = serializers.CharField()
    message = serializers.CharField()
    signature = serializers.CharField()


class GetTaskRequestSerializer(serializers.Serializer):
    hotkey = serializers.CharField()
    message = serializers.CharField()
    signature = serializers.CharField()


class GetTaskResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    warc_paths = serializers.ListField(child=serializers.CharField())
