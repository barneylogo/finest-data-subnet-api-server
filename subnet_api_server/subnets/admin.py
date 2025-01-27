from django.contrib import admin

from .models import Crawl
from .models import Neuron
from .models import ScoreRecord
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
    )
    list_filter = ("date_from", "date_to")
    search_fields = ("name", "dump")
    ordering = ("-date_from",)


@admin.register(WarcFile)
class WarcFileAdmin(admin.ModelAdmin):
    list_display = (
        "warc_path",
        "crawl_dump",
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

    def crawl_dump(self, obj):
        return obj.crawl.dump


@admin.register(Neuron)
class NeuronAdmin(admin.ModelAdmin):
    list_display = ("hotkey", "coldkey", "uid", "created_at", "updated_at")
    search_fields = ("hotkey", "coldkey")
    ordering = ("-created_at",)


# Admin customization for TaskRecord model
@admin.register(TaskRecord)
class TaskRecordAdmin(admin.ModelAdmin):
    list_display = (
        "miner_hotkey",
        "request_block",
        "status",
        "get_warc_files",
        "hf_repo",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("miner__hotkey", "status")
    ordering = ("-created_at",)
    fields = ("miner", "status", "request_block", "hf_repo")

    @admin.display(
        description="Miner Hotkey",
    )
    def miner_hotkey(self, obj):
        hotkey = obj.miner.hotkey
        return f"{hotkey[:5]}...{hotkey[-5:]}"

    @admin.display(
        description="Warc Files",
    )
    def get_warc_files(self, obj):
        return ", ".join(
            f"{warc_file.warc_path} (ID: {warc_file.id})"
            for warc_file in obj.warc_files.all()
        )


@admin.register(ScoreRecord)
class ScoreRecordAdmin(admin.ModelAdmin):
    list_display = (
        "validator_hotkey",
        "task_record_id",
        "score",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at",)
    search_fields = ("validator__hotkey", "task_record__validator__hotkey")
    ordering = ("-created_at",)

    @admin.display(
        description="Validator Hotkey",
    )
    def validator_hotkey(self, obj):
        hotkey = obj.validator.hotkey
        return f"{hotkey[:5]}...{hotkey[-5:]}"

    @admin.display(
        description="Task Record",
    )
    def task_record_id(self, obj):
        return obj.task_record.id
