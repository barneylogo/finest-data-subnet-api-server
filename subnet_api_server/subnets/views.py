from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subnet_api_server.common.models import StatusEnum
from subnet_api_server.subnets.models import Neuron
from subnet_api_server.subnets.models import TaskRecord
from subnet_api_server.subnets.models import WarcFile
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
                    existing_task.request_time = timezone.now()
                    existing_task.save()

                    warc_files = WarcFile.objects.filter(
                        pk__in=existing_task.warc_file_ids,
                    )
                    warc_paths = [wf.warc_path for wf in warc_files]

                    return Response(
                        {
                            "message": "You already have a pending task.",
                            "warc_paths": warc_paths,
                        },
                        status=status.HTTP_200_OK,
                    )

                last_completed_task = (
                    TaskRecord.objects.filter(
                        neuron=neuron,
                        status=StatusEnum.completed.name,
                    )
                    .order_by("-request_time")
                    .first()
                )

                if (
                    last_completed_task
                    and last_completed_task.request_time.date() == timezone.now().date()
                ):
                    return Response(
                        {"detail": "You are limited to one task request per day"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                available_warc_files = WarcFile.objects.filter(
                    status=StatusEnum.available.name,
                ).order_by("?")[:4]
                if not available_warc_files:
                    return Response(
                        {"detail": "No WARC files are currently available."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                for warc_file in available_warc_files:
                    warc_file.status = StatusEnum.pending.name
                    warc_file.save()

                warc_file_ids = [wf.pk for wf in available_warc_files]
                new_task = TaskRecord.objects.create(
                    neuron=neuron,
                    request_time=timezone.now(),
                    status=StatusEnum.pending.name,
                    warc_file_ids=warc_file_ids,
                )

                new_task.save()

                warc_paths = [wf.warc_path for wf in available_warc_files]

                return Response(
                    {
                        "message": "success",
                        "warc_paths": warc_paths,
                    },
                )
        except Exception as e:
            return Response({"message": str(e)}, status=500)
