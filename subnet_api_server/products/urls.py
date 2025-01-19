from django.urls import path

from subnet_api_server.products.views import GetProductsView

urlpatterns = [
    path("<int:count>/", GetProductsView.as_view(), kwargs={"count": 0}),
]
