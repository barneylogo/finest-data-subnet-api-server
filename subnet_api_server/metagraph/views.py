from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subnet_api_server.common.services import BittensorService


class GetNodesView(APIView):
    @extend_schema(
        description="Get all nodes.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={
                            "nodes": [1, 2, 3],  # Example list of node IDs
                            "total": 3,
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def get(self, request):
        try:
            nodes = BittensorService.get_neurons()
            return Response(
                {"nodes": nodes, "total": len(nodes)},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetValidatorsView(APIView):
    @extend_schema(
        description="Get all validators.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={"validators": [1, 2, 3], "total": 3},
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
                {"validators": nodes, "total": len(nodes)},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetNodeByUidView(APIView):
    @extend_schema(
        description="Get a node by UID.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={"uid": 1, "hotkey": "hotkey", "name": "name"},
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def get(self, request, uid):
        try:
            nodes = BittensorService.get_neurons()
            node = next((node for node in nodes if node["uid"] == uid), None)
            if node:
                return Response(node, status=status.HTTP_200_OK)
            return Response(
                {"message": f"Node with uid {uid} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetSubnetStatsView(APIView):
    @extend_schema(
        description="Get subnet stats.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={"stats": {"total": 3, "items": [1, 2, 3]}},
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def get(self, request):
        try:
            stats = BittensorService.get_subnet_stats()
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
