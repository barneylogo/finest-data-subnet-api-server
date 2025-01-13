from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from subnet_api_server.common.services import BittensorService


class GetNodesView(APIView):

    def get(self, request):
        try:
            metagraph = BittensorService.get_metagraph()
            nodes = metagraph.neurons
            return Response(
                {"nodes": nodes, "total": len(nodes)}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
