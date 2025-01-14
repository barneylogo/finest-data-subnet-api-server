from django.urls import path

from subnet_api_server.metagraph.views import GetNodesView

urlpatterns = [
    path("nodes/", GetNodesView.as_view(), name="get_all_nodes"),
    path("node/<int:uid>/", GetNodesView.as_view(), name="get_node_by_uid"),
]
