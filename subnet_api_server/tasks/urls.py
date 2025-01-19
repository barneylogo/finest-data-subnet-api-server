from django.urls import path

from subnet_api_server.tasks.views import GetTasksView

urlpatterns = [
    path("", GetTasksView.as_view()),
]
