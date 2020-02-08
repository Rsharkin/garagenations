"""
    Sends pickup reminder to customer for whom driver is assigned and booking is not in followup.
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models.booking import Booking, BookingPackage
from core.managers.generalManager import send_custom_notification
from core.utils import _convert_to_given_timezone, make_datetime_timezone_aware_convert_to_utc
from core.models.message import Messages
from core.models.master import Notifications
from django.db.models import Q
from core.utils import format_datetime_for_grid, format_datetime_for_msg
import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = "Script:: PICKUP_REMINDER:: Trigger email to customer for next day's pickup"

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: PICKUP_REMINDER:: Script started - current_time: %s" % current_time)

        subject = None

        # pickup time in next day
        current_context_time = _convert_to_given_timezone(timezone.now(), settings.TIME_ZONE)
        date_for_tomorrow_in_current_context = current_context_time + timezone.timedelta(days=1)
        start_time = make_datetime_timezone_aware_convert_to_utc(str(date_for_tomorrow_in_current_context.date())+" 00:00:00", "+0530")
        end_time = start_time + timezone.timedelta(hours=24)

        logger.info("Script:: PICKUP_REMINDER:: start_time: %s - end_Time: %s" % (start_time, end_time))
        try:
            pickup_in_next_day_bookings = Booking.objects.select_related('user')\
                .filter(status_id=3, pickup_time__range =[start_time, end_time])\
                .exclude(Q(ops_status_id=8) | Q(pickup_driver_id__isnull=True))

            if not pickup_in_next_day_bookings:
                logger.exception("Script:: PICKUP_REMINDER:: No Bookings to send notifications to.")

            for booking in pickup_in_next_day_bookings:
                try:
                    pickup_time = format_datetime_for_grid(booking.pickup_time)
                    if pickup_time and format_datetime_for_grid(booking.pickup_slot_end_time):
                        pickup_time = pickup_time + ' - ' + format_datetime_for_msg(booking.pickup_slot_end_time)

                    booking_packages = BookingPackage.objects.filter(booking=booking)
                    package_taken = []
                    for item in booking_packages:
                        package_taken.append(item.package.package.name)

                    logger.info("Script:: PICKUP_REMINDER:: Booking Id: %s" % booking.id)
                    template_vars = {
                        'bookingId': booking.id,
                        'customer_name': booking.user.name,
                        'phone': booking.user.phone,
                        'email': booking.user.email,
                        'pickup_driver_name': booking.pickup_driver.name if booking.pickup_driver else '',
                        'pickup_driver_phone': booking.pickup_driver.ops_phone if booking.pickup_driver else '',
                        'pickup_time_details': pickup_time if pickup_time else '',
                        'package_details': ', '.join(package_taken),
                        'app_redirect_url': settings.BUMPER_APP_URL_THROUGH_APP_REDIRECT_URL % str(booking.id)
                    }

                    messages = Messages.objects.filter(booking_id=booking.id)

                    if booking.is_doorstep:
                        email_notification = Notifications.objects.get(name='USER_EMAIL_PICKUP_REMINDER_DOOR')
                        sms_notification = Notifications.objects.get(name='USER_SMS_PICKUP_REMINDER_ATDOOR')
                        push_notification = Notifications.objects.get(name='USER_PUSH_PICKUP_REMINDER_ATDOOR')
                    else:
                        email_notification = Notifications.objects.get(name='USER_EMAIL_PICKUP_REMINDER')
                        sms_notification = Notifications.objects.get(name='USER_SMS_PICKUP_REMINDER')
                        push_notification = Notifications.objects.get(name='USER_EMAIL_PICKUP_REMINDER')

                    if not messages.filter(notification=email_notification).exists():
                        logger.info("Script:: PICKUP_REMINDER:: Sending Email")
                        send_custom_notification(email_notification.name, template_vars,
                                                 params_dict={'booking_id': booking.id}, user=booking.user)
                    else:
                        logger.info("Script:: PICKUP_REMINDER:: Not sending email as already sent.")

                    if not messages.filter(notification=sms_notification).exists():
                        logger.info("Script:: PICKUP_REMINDER:: Sending SMS")
                        send_custom_notification(sms_notification.name, template_vars,
                                                 params_dict={'booking_id': booking.id}, user=booking.user)
                    else:
                        logger.info("Script:: PICKUP_REMINDER:: Not sending SMS as already sent.")

                    if not messages.filter(notification=push_notification).exists():
                        logger.info("Script:: PICKUP_REMINDER:: Sending PUSH")
                        send_custom_notification(push_notification.name, template_vars,
                                                 params_dict={'booking_id': booking.id}, user=booking.user)
                    else:
                        logger.info("Script:: PICKUP_REMINDER:: Not sending PUSH as already sent.")

                    logger.info("Script:: PICKUP_REMINDER:: Processed")
                except:
                    logger.exception("Script:: PICKUP_REMINDER:: Failed")
        except:
            logger.exception("Script:: PICKUP_REMINDER:: Failed to process to bookings")