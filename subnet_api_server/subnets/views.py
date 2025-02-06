from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subnet_api_server.common.models import StatusEnum
from subnet_api_server.common.services import BittensorService
from subnet_api_server.subnets.models import Neuron
from subnet_api_server.subnets.models import ScoreRecord
from subnet_api_server.subnets.models import TaskRecord
from subnet_api_server.subnets.models import WarcFile
from subnet_api_server.subnets.serializers import CheckTaskRequestSerializer
from subnet_api_server.subnets.serializers import CheckTaskResponseSerializer
from subnet_api_server.subnets.serializers import FinishTaskRequestSerializer
from subnet_api_server.subnets.serializers import GetTaskRequestSerializer
from subnet_api_server.subnets.serializers import GetTaskResponseSerializer
from subnet_api_server.subnets.serializers import ReportScoreRequestSerializer
from subnet_api_server.subnets.utils import verify_signature


class GetTaskViewSet(APIView):
    @extend_schema(
        description="Get a task by hotkey.",
        request=GetTaskRequestSerializer,
        responses={
            200: GetTaskResponseSerializer,
        },
    )
    def post(self, request):
        try:
            serializer = GetTaskRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            hotkey = serializer.validated_data.get("hotkey")
            message = serializer.validated_data.get("message")
            signature = serializer.validated_data.get("signature")

            if not hotkey or not message or not signature:
                return Response(
                    {"message": "Hotkey, message, and signature are required"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not verify_signature(hotkey, message, signature):
                return Response(
                    {"message": "Invalid signature"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                metagraph = BittensorService.get_metagraph()
                neuron = next((n for n in metagraph.neurons if n.hotkey == hotkey), None)

                if not neuron:
                    return Response(
                        {"message": "Miner's hotkey is not registered."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                
                neuron_instance, _ = Neuron.objects.update_or_create(
                    hotkey=neuron.hotkey,
                    uid=neuron.uid,
                    coldkey=neuron.coldkey,
                )

            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            existing_task = (
                TaskRecord.objects.filter(
                    miner=neuron_instance,
                    status=StatusEnum.pending.name,
                )
                .order_by("-created_at")
                .first()
            )

            if existing_task:
                warc_files = existing_task.warc_files.all()
                warc_paths = [wf.warc_path for wf in warc_files]

                task_serializer = GetTaskResponseSerializer(
                    {
                        "message": "You already have a pending task.",
                        "warc_paths": warc_paths,
                    },
                )
                return Response(task_serializer.data, status=status.HTTP_200_OK)

            last_completed_task = (
                TaskRecord.objects.filter(
                    miner=neuron_instance,
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
                    status=status.HTTP_404_NOT_FOUND,
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

            [wf.pk for wf in available_warc_files]
            new_task = TaskRecord.objects.create(
                miner=neuron_instance,
                request_block=BittensorService.get_current_block(),
                status=StatusEnum.pending.name,
            )

            new_task.warc_files.set(available_warc_files)
            new_task.save()

            warc_paths = [wf.warc_path for wf in available_warc_files]
            task_serializer = GetTaskResponseSerializer(
                {
                    "message": "success",
                    "warc_paths": warc_paths,
                },
            )
            return Response(task_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FinishTaskViewSet(APIView):
    @extend_schema(
        description="Finish a task by UID.",
        request=FinishTaskRequestSerializer,
        responses={
            200: {"message": "Task finished"},
        },
    )
    def post(self, request):
        try:
            serializer = FinishTaskRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            hotkey = serializer.validated_data.get("hotkey")
            hf_repo = serializer.validated_data.get("hf_repo")
            message = serializer.validated_data.get("message")
            signature = serializer.validated_data.get("signature")

            if not hotkey or not hf_repo or not message or not signature:
                return Response(
                    {"message": "Hotkey, hf_repo, message, and signature are required"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not verify_signature(hotkey, message, signature):
                return Response(
                    {"message": "Invalid signature"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            pending_task = TaskRecord.objects.filter(
                miner__hotkey=hotkey,
                status=StatusEnum.pending.name,
            ).first()

            if not pending_task:
                return Response(
                    {"message": "Not found pending task"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            pending_task.status = StatusEnum.completed.name
            pending_task.hf_repo = hf_repo
            pending_task.save()

            warc_files = pending_task.warc_files.all()
            for warc_file in warc_files:
                warc_file.status = StatusEnum.completed.name
                warc_file.save()

            return Response({"message": "Task finished"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckTaskViewSet(APIView):
    @extend_schema(
        description="Check the status of a task by UID.",
        request=CheckTaskRequestSerializer,
        responses={
            200: CheckTaskResponseSerializer,
        },
    )
    def post(self, request):
        try:
            serializer = CheckTaskRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"message": "Invalid request"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            uid = serializer.validated_data.get("uid")

            completed_task = (
                TaskRecord.objects.filter(
                    miner__uid=uid,
                    status=StatusEnum.completed.name,
                )
                .order_by("-updated_at")
                .first()
            )
            if completed_task:
                warc_files = completed_task.warc_files.all()

                warc_paths = [wf.warc_path for wf in warc_files]

                serializer = CheckTaskResponseSerializer(
                    {
                        "message": "success",
                        "task_id": completed_task.id,
                        "warc_files": warc_paths,
                        "request_block": completed_task.request_block,
                    },
                )
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(
                {"message": "Task not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReportScoreViewSet(APIView):
    @extend_schema(
        description="Report the score of a task by UID.",
        request=ReportScoreRequestSerializer,
        responses={
            200: {"message": "Score reported"},
        },
    )
    def post(self, request):
        try:
            serializer = ReportScoreRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            hotkey = serializer.validated_data.get("hotkey")
            task_id = serializer.validated_data.get("task_id")
            score = serializer.validated_data.get("score")
            signature = serializer.validated_data.get("signature")
            if not hotkey or not task_id or not score or not signature:
                return Response(
                    {"message": "Hotkey, task ID, score, and signature are required"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if not verify_signature(hotkey, str(task_id), signature):
                return Response({"message": "Invalid signature"}, status=400)

            task = TaskRecord.objects.get(pk=task_id)
            
            try:
                validators = BittensorService.get_validators()
                validator = next((v for v in validators if v["hotkey"] == hotkey), None)

                if not validator:
                    return Response(
                        {"message": "Validator is not registered or has insufficient stake to set weights on the subnet."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                
                neuron_instance, _ = Neuron.objects.update_or_create(
                    hotkey=validator["hotkey"],
                    uid=validator["uid"],
                    coldkey=validator["coldkey"],
                )

            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            score_record, created = ScoreRecord.objects.get_or_create(
                validator=neuron_instance,
                task_record=task,
                defaults={"score": score},
            )

            if not created:
                score_record.score = score
                score_record.save()

            return Response({"message": "Score reported"}, status=200)
        except Exception as e:
            return Response({"message": str(e)}, status=500)
