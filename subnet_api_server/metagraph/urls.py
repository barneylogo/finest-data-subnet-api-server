from django.urls import path

from subnet_api_server.metagraph.views import GetNodesView

urlpatterns = [
    path("nodes/", GetNodesView.as_view()),
    # path("node/<int:node_id>/", GetNodeView.as_view()),
]
