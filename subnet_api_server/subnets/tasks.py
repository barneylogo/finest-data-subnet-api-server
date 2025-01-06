from datetime import datetime
from datetime import timedelta

from celery import shared_task

from subnet_api_server.common.models import StatusEnum
from subnet_api_server.subnets.models import TaskRecord
from subnet_api_server.subnets.models import WarcFile


@shared_task
def update_pending_tasks():
    eight_hours_ago = datetime.now() - timedelta(hours=8)

    pending_tasks = TaskRecord.objects.filter(
        status=StatusEnum.pending.name,
        request_time__lte=eight_hours_ago,
    )

    for task in pending_tasks:
        pending_warc_files = WarcFile.objects.filter(id__in=task.warc_file_ids)
        for warc_file in pending_warc_files:
            warc_file.status = StatusEnum.available.name
            warc_file.save()

        task.status = StatusEnum.failed.name
        task.save()
