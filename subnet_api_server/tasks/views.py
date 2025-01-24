from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subnet_api_server.subnets.models import TaskRecord
from subnet_api_server.tasks.serializers import TaskRecordRequestSerializer
from subnet_api_server.tasks.serializers import TaskRecordResponseSerializer


class GetTasksView(APIView):
    @extend_schema(
        description="Get tasks by hotkey.",
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
                TaskRecord.objects.select_related("neuron")
                .all()
                .order_by("-created_at")
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
