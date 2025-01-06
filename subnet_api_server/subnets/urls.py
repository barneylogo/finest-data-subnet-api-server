from django.urls import path

from .views import GetTaskViewSet

urlpatterns = [
    path("get-task/", GetTaskViewSet.as_view()),
]
