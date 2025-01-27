from django.core.management.base import BaseCommand

from subnet_api_server.subnets.models import StatusEnum
from subnet_api_server.subnets.models import WarcFile


class Command(BaseCommand):
    command_help = "Update all WarcFile records"

    def handle(self, *args, **kwargs):
        try:
            # Delete all WarcFile records
            pending_warc_files = WarcFile.objects.filter(
                status=StatusEnum.completed.name,
            ).all()
            for warc_file in pending_warc_files:
                warc_file.status = StatusEnum.available.name
                warc_file.save()
            self.stdout.write(f"Updated {pending_warc_files.count()} WARC files.")
        except Exception as e:
            self.stdout.write(f"Error deleting WARC files: {e!s}")
