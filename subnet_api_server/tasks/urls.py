from django.urls import path

from subnet_api_server.tasks.views import GetTasksView, GetScoresByTaskView

urlpatterns = [
    path("", GetTasksView.as_view()),
    path("<int:task_id>/", GetScoresByTaskView.as_view()),
]
