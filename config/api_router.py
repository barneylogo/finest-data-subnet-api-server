from django.conf import settings
from django.urls import include
from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularRedocView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

urls = [
    path("subnets/", include("subnet_api_server.subnets.urls")),
    path("metagraph/", include("subnet_api_server.metagraph.urls")),
    path("stats/", include("subnet_api_server.stats.urls")),
    path("products/", include("subnet_api_server.products.urls")),
    path("tasks/", include("subnet_api_server.tasks.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api:schema"),
        name="docs",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="api:schema"),
        name="redoc",
    ),
]

app_name = "api"

urlpatterns = urls
