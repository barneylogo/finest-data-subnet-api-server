from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subnet_api_server.subnets.models import TaskRecord, ScoreRecord
from subnet_api_server.tasks.serializers import (
    TaskRecordRequestSerializer,
    ScoresResponseSerializer,
)
from subnet_api_server.tasks.serializers import TaskRecordResponseSerializer


class GetTasksView(APIView):
    @extend_schema(
        description="Get all tasks.",
        request=TaskRecordRequestSerializer,
        responses={
            200: TaskRecordRequestSerializer,
        },
    )
    def get(self, request):
        try:
            count = request.query_params.get("count", 0)
            if count is not None:
                count = int(count)

            tasks = (
                TaskRecord.objects.select_related("miner").all().order_by("-created_at")
            )
            if count:
                tasks = tasks[:count]
            serialized_tasks = TaskRecordResponseSerializer(tasks, many=True).data
            return Response(
                {
                    "total": len(serialized_tasks),
                    "items": serialized_tasks,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetScoresByTaskView(APIView):
    @extend_schema(
        description="Get all scores for a given task.",
        request=TaskRecordRequestSerializer,
        responses={
            200: TaskRecordRequestSerializer,
        },
    )
    def get(self, request, task_id: int):
        try:
            count = request.query_params.get("count", 0)
            if count is not None:
                count = int(count)

            score_records = (
                ScoreRecord.objects.select_related("task_record")
                .select_related("validator")
                .filter(task_record_id=task_id)
                .order_by("-created_at")
            )
            if count:
                score_records = score_records[:count]

            serialized_scores = ScoresResponseSerializer(score_records, many=True).data
            return Response(
                {
                    "total": len(serialized_scores),
                    "items": serialized_scores,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
