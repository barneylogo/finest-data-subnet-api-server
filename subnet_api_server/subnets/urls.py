from django.urls import path

from .views import CheckTaskViewSet
from .views import FinishTaskViewSet
from .views import GetTaskViewSet
from .views import ReportScoreViewSet

urlpatterns = [
    path("get-task/", GetTaskViewSet.as_view()),
    path("finish-task/", FinishTaskViewSet.as_view()),
    path("check-task/", CheckTaskViewSet.as_view()),
    path("report-score/", ReportScoreViewSet.as_view()),
]
