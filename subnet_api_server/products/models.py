from django.db import models

from subnet_api_server.common.models import Common
from subnet_api_server.subnets.models import Crawl


class Product(Common):
    crawl = models.ForeignKey(
        Crawl,
        related_name="products",
        on_delete=models.CASCADE,
    )
    hf_repo = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    rows = models.IntegerField()
    tokens = models.IntegerField()

    class Meta:
        db_table = "products"
