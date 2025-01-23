from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
                        value={"total": 3, "items": [1, 2, 3]},
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


class GetWeightsView(APIView):
    @extend_schema(
        description="Get all weights.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={
                            "validators": [1, 2, 3],
                            "miners": [1, 2, 3],
                            "weights": {
                                1: {1: 1, 2: 2, 3: 3},
                                2: {1: 1, 2: 2, 3: 3},
                                3: {1: 1, 2: 2, 3: 3},
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
            validator_uids = [validator["uid"] for validator in validators]

            # Initialize weights dictionary
            weights = {miner["uid"]: {} for miner in miners}

            # Get the latest task record for each miner
            latest_task_records = (
                TaskRecord.objects.select_related("neuron")
                .order_by("neuron", "-created_at")
                .distinct("neuron")
            )

            if len(miners) == 0 or len(validators) == 0:
                return Response(
                    {
                        "validators": validator_uids,
                        "miners": miners,
                        "weights": weights,
                    },
                    status=status.HTTP_200_OK,
                )

            # Get scores for the latest task records
            for task_record in latest_task_records:
                miner_neuron = task_record.neuron
                scores = ScoreRecord.objects.filter(task_record=task_record)

                for score_record in scores:
                    validator_neuron = score_record.neuron
                    weights[miner_neuron.uid][validator_neuron.uid] = score_record.score

            return Response(
                {"validators": validator_uids, "miners": miners, "weights": weights},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
