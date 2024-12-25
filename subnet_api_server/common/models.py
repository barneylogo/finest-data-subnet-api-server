import enum

from django.db import models


class Common(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StatusEnum(enum.Enum):
    pending = "pending", "Pending"
    available = "available", "Available"
    completed = "completed", "Completed"
    failed = "failed", "Failed"

    @classmethod
    def choices(cls):
        return [(status.value[0], status.value[1]) for status in cls]
