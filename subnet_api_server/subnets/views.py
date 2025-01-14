from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subnet_api_server.common.models import StatusEnum
from subnet_api_server.common.services import BittensorService
from subnet_api_server.subnets.models import Neuron
from subnet_api_server.subnets.models import TaskRecord
from subnet_api_server.subnets.models import WarcFile
from subnet_api_server.subnets.serializers import CheckTaskSerializer
from subnet_api_server.subnets.serializers import GetTaskSerializer
from subnet_api_server.subnets.tasks import update_pending_tasks


class GetTaskViewSet(APIView):
    def post(self, request):
        try:
            hotkey = request.data.get("hotkey")
            if not hotkey:
                return Response({"message": "Hotkey is required"}, status=400)

            with transaction.atomic():
                update_pending_tasks.delay()
                try:
                    neuron = Neuron.objects.get(hotkey=hotkey)
                except Neuron.DoesNotExist:
                    return Response(
                        {"detail": "Hotkey not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                existing_task = TaskRecord.objects.filter(
                    neuron=neuron,
                    status=StatusEnum.pending.name,
                ).first()

                if existing_task:
                    warc_files = WarcFile.objects.filter(
                        pk__in=existing_task.warc_file_ids,
                    )
                    warc_paths = [wf.warc_path for wf in warc_files]

                    task_serializer = GetTaskSerializer(
                        {
                            "message": "You already have a pending task.",
                            "warc_paths": warc_paths,
                        },
                    )
                    if task_serializer.is_valid():
                        return Response(task_serializer.data, status=status.HTTP_200_OK)
                    return Response({"message": "Invalid data"}, status=400)

                last_completed_task = (
                    TaskRecord.objects.filter(
                        neuron=neuron,
                        status=StatusEnum.completed.name,
                    )
                    .order_by("-request_block")
                    .first()
                )

                if (
                    last_completed_task
                    and last_completed_task.updated_at.date() == timezone.now().date()
                ):
                    return Response(
                        {"message": "You are limited to one task request per day"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                available_warc_files = WarcFile.objects.filter(
                    status=StatusEnum.available.name,
                ).order_by("?")[:4]
                if not available_warc_files:
                    return Response(
                        {"message": "No WARC files are currently available."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                for warc_file in available_warc_files:
                    warc_file.status = StatusEnum.pending.name
                    warc_file.save()

                warc_file_ids = [wf.pk for wf in available_warc_files]
                new_task = TaskRecord.objects.create(
                    neuron=neuron,
                    request_block=BittensorService.get_current_block(),
                    status=StatusEnum.pending.name,
                    warc_file_ids=warc_file_ids,
                )

                new_task.save()

                warc_paths = [wf.warc_path for wf in available_warc_files]
                task_serializer = GetTaskSerializer(
                    {
                        "message": "success",
                        "warc_paths": warc_paths,
                    },
                )
                return Response(task_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=500)


class FinishTaskViewSet(APIView):
    def post(self, request):
        try:
            hotkey = request.data.get("hotkey")
            hf_repo = request.data.get("hf_repo")
            if not hotkey:
                return Response({"message": "Hotkey is required"}, status=400)

            task = TaskRecord.objects.get(
                neuron__hotkey=hotkey,
                status=StatusEnum.pending.name,
            )
            if not task:
                return Response({"message": "Not found pending task"}, status=404)

            task.status = StatusEnum.completed.name
            task.hf_repo = hf_repo
            task.save()

            for warc_file_id in task.warc_file_ids:
                warc_file = WarcFile.objects.get(pk=warc_file_id)
                warc_file.status = StatusEnum.completed.name
                warc_file.save()

            return Response({"message": "Task finished"}, status=200)
        except Exception as e:
            return Response({"message": str(e)}, status=500)


class CheckTaskViewSet(APIView):
    def post(self, request):
        try:
            uid = request.data.get("uid")
            if not uid:
                return Response({"message": "UID is required"}, status=400)

            completed_task = (
                TaskRecord.objects.filter(
                    neuron__uid=uid,
                    status=StatusEnum.completed.name,
                )
                .order_by("-updated_at")
                .first()
            )
            if completed_task:
                warc_files = WarcFile.objects.filter(
                    pk__in=completed_task.warc_file_ids,
                )
                warc_paths = [wf.warc_path for wf in warc_files]

                serializer = CheckTaskSerializer(
                    {
                        "message": "success",
                        "warc_files": warc_paths,
                        "request_block": completed_task.request_block,
                    },
                )
                return Response(serializer.data, status=200)

            return Response({"message": "Task not found"}, status=404)

        except Exception as e:
            return Response({"message": str(e)}, status=500)
