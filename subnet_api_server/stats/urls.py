from django.urls import path

from subnet_api_server.stats.views import GetValidatorsView

urlpatterns = [
    path("validators/", GetValidatorsView.as_view()),
]
