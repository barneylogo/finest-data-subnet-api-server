from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from subnet_api_server.common.services import BittensorService


class GetValidatorsView(APIView):
    def get(self, request):
        try:
            nodes = BittensorService.get_validators()
            return Response(
                {"total": len(nodes), "items": nodes},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
