from django.urls import path

from subnet_api_server.stats.views import GetValidatorsView, GetScoresView

urlpatterns = [
    path("validators/", GetValidatorsView.as_view()),
    path("scores/", GetScoresView.as_view()),
]
