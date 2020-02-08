"""
Remove media files already uploaded to S3
"""
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from core.models.common import Media
import glob, os
import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = 'Script:: DAILY_MEDIA_CLEANUP:: Remove media files already uploaded to s3'

    def handle(self, *args, **options):
        logger.info("Script:: DAILY_MEDIA_CLEANUP:: Script started - current_time: %s", timezone.now())
        try:
            os.chdir(settings.MEDIA_ROOT)
            media = Media.objects.filter(uploaded_to_s3=True, created_at__lte=datetime.now() - timedelta(days=3))
            for m in media:
                for file in glob.glob(m.file.name.split('/')[-1]):
                    logger.info("Script:: DAILY_MEDIA_CLEANUP:: Removed media file: %s", file)
                    os.remove(file)
        except:
            logger.exception("Script:: DAILY_MEDIA_CLEANUP:: Failed to cleanup media files")
        logger.info("Script:: DAILY_MEDIA_CLEANUP:: Script ended")
