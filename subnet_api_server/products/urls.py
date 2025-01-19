from django.urls import path

from subnet_api_server.products.views import GetProductsView

urlpatterns = [
    path("", GetProductsView.as_view()),
]
