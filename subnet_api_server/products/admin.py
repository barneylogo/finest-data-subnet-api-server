from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "crawl",
        "hf_repo",
        "name",
        "description",
        "rows",
        "tokens",
    )
    list_filter = ("crawl",)
    search_fields = ("name", "description")
    ordering = ("-created_at",)
