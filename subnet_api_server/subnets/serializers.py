from rest_framework import serializers


# Define a serializer for the response data
class CheckTaskSerializer(serializers.Serializer):
    message = serializers.CharField()
    task_id = serializers.IntegerField()
    warc_files = serializers.ListField(child=serializers.CharField())
    request_block = serializers.IntegerField()


class GetTaskSerializer(serializers.Serializer):
    message = serializers.CharField()
    warc_paths = serializers.ListField(child=serializers.CharField())
