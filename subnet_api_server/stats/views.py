from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subnet_api_server.common.models import StatusEnum
from subnet_api_server.common.services import BittensorService
from subnet_api_server.subnets.models import ScoreRecord
from subnet_api_server.subnets.models import TaskRecord


class GetValidatorsView(APIView):
    @extend_schema(
        description="Get all validators.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={
                            "total": 2,
                            "items": [
                                {
                                    "uid": 0,
                                    "hotkey": "5Ckr36PvmVU78dQXwVSkhy1dXrh4ZaUD8Y5Q9qjjHK7reJXq",
                                    "stake": 33797.542431213,
                                    "validator_trust": 0.9999847409781033,
                                    "rank": 0,
                                    "incentive": 0,
                                    "emission": 40.24940512,
                                    "active": True,
                                    "last_update": 3679701,
                                },
                                {
                                    "uid": 1,
                                    "hotkey": "5Cvzo77XcAUnHipqWos5SQr8uLUD9ndKykj9565PgE3MW4jW",
                                    "stake": 776.224946983,
                                    "validator_trust": 0.9999847409781033,
                                    "rank": 0,
                                    "incentive": 0,
                                    "emission": 40.24940512,
                                    "active": True,
                                    "last_update": 3679701,
                                },
                            ],
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def get(self, request):
        try:
            nodes = BittensorService.get_validators()
            return Response(
                {"total": len(nodes), "items": nodes},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetScoresView(APIView):
    @extend_schema(
        description="Retrieve scores for each miner's most recent completed task.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={
                            "validators": [0, 3],
                            "miners": [1, 2, 4, 5],
                            "scores": {
                                1: {0: 3320, 3: 1150},
                                2: {3: 2238},
                                4: {0: 2384},
                                5: {0: 3215, 3: 2178},
                            },
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def get(self, request):
        try:
            miners = BittensorService.get_miners()
            validators = BittensorService.get_validators()
            miner_uids = [miner["uid"] for miner in miners]
            validator_uids = [validator["uid"] for validator in validators]

            # Get the latest completed task record for each miner
            latest_task_records = (
                TaskRecord.objects.filter(
                    status=StatusEnum.completed.name, miner__uid__in=miner_uids
                )
                .select_related("miner")
                .order_by("miner", "-created_at")
                .distinct("miner")
            )

            # Retrieve scores for the latest task records
            score_records = (
                ScoreRecord.objects.filter(
                    task_record__in=latest_task_records,
                    validator__uid__in=validator_uids,
                )
                .select_related("task_record__miner", "validator")
                .values("task_record__miner__uid", "validator__uid", "score")
            )

            # Organize scores into the desired format
            scores = {}
            for record in score_records:
                miner_uid = record["task_record__miner__uid"]
                validator_uid = record["validator__uid"]
                score = record["score"]
                if miner_uid not in scores:
                    scores[miner_uid] = {}
                scores[miner_uid][validator_uid] = score

            return Response(
                {
                    "validators": list(validator_uids),
                    "miners": list(miners),
                    "scores": scores,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
