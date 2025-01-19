from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from subnet_api_server.products.serializers import ProductSerializer
from subnet_api_server.subnets.models import Product


class GetProductsView(APIView):
    def get(self, request):
        try:
            count = request.query_params.get("count", 0)
            if count is not None:
                count = int(count)
            products = Product.objects.all().order_by("-created_at")
            if count:
                products = products[:count]
            serialized_products = ProductSerializer(products, many=True).data

            return Response(
                {"total": len(serialized_products), "items": serialized_products},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
