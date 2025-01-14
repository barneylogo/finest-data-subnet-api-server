from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from subnet_api_server.common.services import BittensorService


class GetNodesView(APIView):
    def get(self, request):
        try:
            nodes = BittensorService.get_neurons()
            return Response(
                {"nodes": nodes, "total": len(nodes)},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetNodeByUidView(APIView):
    def get(self, request, uid):
        try:
            nodes = BittensorService.get_neurons()
            node = next((node for node in nodes if node["uid"] == uid), None)
            if node:
                return Response(node, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": f"Node with uid {uid} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
