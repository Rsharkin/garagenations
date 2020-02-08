"""
    Send summary of daily alerts to ops Team.
"""
from django.conf import settings
from core.utils import _convert_to_given_timezone, make_datetime_timezone_aware_convert_to_utc
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models.booking import BookingAlertTriggerStatus
from core.models.master import Notifications
from services.email_service import NewEmailService
import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    help = 'Script:: OPS_ALERTS_DAILY_SUMMARY:: Trigger email to ops for different status'
    can_import_settings = True

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: OPS_ALERTS_DAILY_SUMMARY:: Script started - current_time: %s" % current_time)

        current_context_time = _convert_to_given_timezone(timezone.now(), settings.TIME_ZONE)
        start_time = make_datetime_timezone_aware_convert_to_utc(str(current_context_time.date()) + " 00:00:00","+0530")
        end_time = make_datetime_timezone_aware_convert_to_utc(str(current_context_time.date()) + " 23:59:59", "+0530")
        logger.info("Script:: OPS_ALERTS_DAILY_SUMMARY:: start_time: %s - end_Time: %s" % (start_time, end_time))

        try:
            ops_alerts_raised = BookingAlertTriggerStatus.objects.select_related('alert_type')\
                .filter(created_at__range =[start_time, end_time]).exclude(alert_type_id__in=[1, 2])

            logger.debug('Script:: OPS_ALERTS_DAILY_SUMMARY:: Bookings sent in notification: %s' % ops_alerts_raised)

            notification = Notifications.objects.get(name='OPS_ALERTS_DAILY_SUMMARY')
            cc_address_list = notification.get_cc_list()
            to_address_list = notification.get_to_list()

            email_service = NewEmailService(to_address_list, cc_address_list,
                                            context={'ops_alerts_raised': ops_alerts_raised},
                                            analytic_info={'notification_id': notification.id})

            email_service.send(template_folder_name=notification.template_folder_name)

        except:
            logger.exception("Script:: OPS_ALERTS_DAILY_SUMMARY:: Failed to get bookings to process")