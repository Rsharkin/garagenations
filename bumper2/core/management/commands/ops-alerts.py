"""
Sends email to ops for different alerts
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from core.models.booking import Booking, BookingAlertTriggerStatus
from core.managers.bookingManager import process_booking_alert_notification
from core.models.master import OpsAlertType
import json
import logging
logger = logging.getLogger('bumper.scripts')


def process_bookings(bookings, alert_type):
    for booking in bookings:
        if not BookingAlertTriggerStatus.objects.filter(booking=booking, alert_type=alert_type,
                                                        is_triggered=True).exists():
            logger.info(
                "Script:: OPS_ALERTS:: Trigger type=%s Processing Booking id: %s" % (alert_type.name, booking.id))
            try:
                process_booking_alert_notification(booking, alert_type)
                logger.info("Script:: OPS_ALERTS:: Trigger type=%s sent-Booking id: %s" % (alert_type.name, booking.id))
            except:
                logger.exception("Script:: OPS_ALERTS:: Trigger type=%s failed-Booking id: %s" % (alert_type.name,
                                                                                                  booking.id))


class Command(BaseCommand):
    can_import_settings = True
    help = 'Script:: OPS_ALERTS:: Trigger email to ops for different status'

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: OPS_ALERTS:: Script started - current_time: %s" % current_time)

        try:
            ops_alerts = OpsAlertType.objects.all().select_related('notification')

            for ops_alert in ops_alerts:
                #logger.debug('Processing Ops Alert =%s' % ops_alert)
                filter_dict = json.loads(ops_alert.filter_conditions)
                if ops_alert.time_diff:
                    time_field_val = timezone.now() + timezone.timedelta(minutes=ops_alert.time_diff)

                if ops_alert.time_field_range:
                    filter_dict[ops_alert.time_field] = [timezone.now(), time_field_val]
                else:
                    filter_dict[ops_alert.time_field] = time_field_val

                bookings = Booking.objects.filter(**filter_dict).select_related('user', 'usercar', 'usercar__car_model')
                if ops_alert.exclude_conditions:
                    exclude_dict = json.loads(ops_alert.exclude_conditions)
                    bookings = bookings.exclude(**exclude_dict)

                process_bookings(bookings, ops_alert)
        except:
            logger.exception("Script:: OPS_ALERTS:: Failed to get bookings to process")