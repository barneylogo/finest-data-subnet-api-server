from django.urls import path

from subnet_api_server.stats.views import GetValidatorsView, GetWeightsView

urlpatterns = [
    path("validators/", GetValidatorsView.as_view()),
    path("weights/", GetWeightsView.as_view()),
]
