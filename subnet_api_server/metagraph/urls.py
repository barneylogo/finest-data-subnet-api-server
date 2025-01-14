from django.urls import path

from subnet_api_server.metagraph.views import GetNodesView, GetNodeByUidView

urlpatterns = [
    path("nodes/", GetNodesView.as_view()),
    path("node/<int:uid>/", GetNodeByUidView.as_view()),
]
