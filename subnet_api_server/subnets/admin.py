from django.contrib import admin

from .models import Crawl
from .models import Neuron
from .models import TaskRecord
from .models import WarcFile


@admin.register(Crawl)
class CrawlAdmin(admin.ModelAdmin):
    list_display = (
        "dump",
        "name",
        "timegate",
        "cdx_api",
        "date_from",
        "date_to",
        "warc_size",
        "warc_files",
    )
    list_filter = ("date_from", "date_to")
    search_fields = ("name", "dump")
    ordering = ("-date_from",)


@admin.register(WarcFile)
class WarcFileAdmin(admin.ModelAdmin):
    list_display = (
        "warc_path",
        "crawl",
        "size",
        "date",
        "last_modified",
        "etag",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "date")
    search_fields = ("warc_path", "etag", "crawl__name")
    ordering = ("-created_at",)


@admin.register(Neuron)
class NeuronAdmin(admin.ModelAdmin):
    list_display = ("hotkey", "coldkey", "uid", "created_at", "updated_at")
    search_fields = ("hotkey", "coldkey")
    ordering = ("-created_at",)


# Admin customization for TaskRecord model
@admin.register(TaskRecord)
class TaskRecordAdmin(admin.ModelAdmin):
    list_display = ("neuron", "request_time", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("neuron__hotkey", "status")
    ordering = ("-created_at",)
