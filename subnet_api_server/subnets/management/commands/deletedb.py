from django.core.management.base import BaseCommand
from subnets.models import WarcFile


class Command(BaseCommand):
    command_help = "Remove all WarcFile records"

    def handle(self, *args, **kwargs):
        try:
            # Delete all WarcFile records
            deleted_count, _ = WarcFile.objects.all().delete()
            self.stdout.write(f"Deleted {deleted_count} WARC files.")
        except Exception as e:
            self.stdout.write(f"Error deleting WARC files: {e!s}")
