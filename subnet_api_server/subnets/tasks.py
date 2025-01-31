import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from subnet_api_server.common.models import StatusEnum
from subnet_api_server.common.services import BittensorService
from subnet_api_server.subnets.models import Neuron
from subnet_api_server.subnets.models import TaskRecord
from subnet_api_server.subnets.models import WarcFile

logger = logging.getLogger(__name__)


@shared_task
def mark_stale_tasks_as_failed():
    logger.info("Marking stale tasks as failed")
    stale_time_limit = timezone.now() - timedelta(days=1)
    stale_tasks = TaskRecord.objects.filter(
        status=StatusEnum.pending.name,
        created_at__lt=stale_time_limit,
    )

    if stale_tasks.count() > 0:
        for task in stale_tasks:
            task.status = StatusEnum.failed.name
            task.save()

            warc_files = WarcFile.objects.filter(
                pk__in=task.warc_file_ids,
            )

            for warc_file in warc_files:
                warc_file.status = StatusEnum.available.name
                warc_file.save()


@shared_task
def update_neuron():
    try:
        config = BittensorService.get_config()
        subtensor = BittensorService.get_subtensor()
        metagraph = subtensor.metagraph(netuid=config.netuid)

        for uid in metagraph.uids:
            hotkey = metagraph.hotkeys[uid]
            coldkey = metagraph.coldkeys[uid]
            new_neuron = Neuron.objects.create(
                uid=int(uid),
                hotkey=hotkey,
                coldkey=coldkey,
            )
            print(f"Added neuron: {new_neuron.uid}")
    except Exception as e:
        print(str(e))
