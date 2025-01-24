from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subnet_api_server.products.models import Product
from subnet_api_server.products.serializers import ProductSerializer


class GetProductsView(APIView):
    @extend_schema(
        description="Get all products.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Example Response",
                        value={"total": 3, "items": [1, 2, 3]},
                    ),
                ],
            ),
        },
    )
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
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
