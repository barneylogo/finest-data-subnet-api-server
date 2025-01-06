from django.db import models

from subnet_api_server.common.models import Common
from subnet_api_server.common.models import StatusEnum


class Crawl(Common):
    dump = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    timegate = models.CharField(max_length=255)
    cdx_api = models.CharField(max_length=255)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    warc_size = models.FloatField()

    class Meta:
        db_table = "crawls"


class WarcFile(Common):
    warc_path = models.CharField(max_length=255, unique=True)
    size = models.IntegerField()
    date = models.DateTimeField()
    last_modified = models.DateTimeField()
    etag = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[
            (status.name, status.value[1]) for status in StatusEnum
        ],  # Correct choice tuple structure
        default=StatusEnum.available.name,
    )

    crawl = models.ForeignKey(
        Crawl,
        related_name="warc_files_rel",  # Rename to avoid conflict
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "warc_files"


class Neuron(Common):
    hotkey = models.CharField(max_length=255, unique=True)
    coldkey = models.CharField(max_length=255)
    uid = models.IntegerField()

    class Meta:
        db_table = "neurons"


class TaskRecord(Common):
    neuron = models.ForeignKey(
        Neuron,
        related_name="task_records_rel",  # Rename to avoid conflict
        on_delete=models.CASCADE,
    )
    warc_file_ids = models.JSONField()
    request_block = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            (status.name, status.value[1]) for status in StatusEnum
        ],  # Correct choice tuple structure
        default=StatusEnum.pending.name,
    )

    class Meta:
        db_table = "task_records"
