from django.urls import path

from .views import FinishTaskViewSet
from .views import GetTaskViewSet

urlpatterns = [
    path("get-task/", GetTaskViewSet.as_view()),
    path("finish-task/", FinishTaskViewSet.as_view()),
]
