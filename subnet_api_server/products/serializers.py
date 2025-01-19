from rest_framework import serializers

from subnet_api_server.subnets.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
