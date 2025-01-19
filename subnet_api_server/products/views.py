from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from subnet_api_server.common.services import BittensorService
from subnet_api_server.subnets.models import Product


class GetProductsView(APIView):
    def get(self, request, count):
        try:
            products = Product.objects.all()[:count]

            return Response(
                {"total": len(products), "items": products},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
