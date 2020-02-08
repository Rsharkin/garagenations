"""
    Sends email with list of tomorrow's pickup
"""
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models.booking import Booking, BookingAddress, BookingPackage, BookingPackagePanel
from core.models.master import Notifications, Package
from core.utils import _convert_to_given_timezone, make_datetime_timezone_aware_convert_to_utc, format_datetime_for_grid
from services.email_service import NewEmailService
import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = 'Script:: PICKUP_SUMMARY:: Trigger email to ops for different status'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--reminder',
            action='store_true',
            dest='reminder',
            default=False,
            help='Change subject to reminder mail',
        )

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: PICKUP_SUMMARY:: Script started - current_time: %s" % current_time)

        override_subject = None
        if options['reminder']:
            override_subject = "Reminder to set Tomorrow's Pickup"

        # pickup time in next day
        current_context_time = _convert_to_given_timezone(timezone.now(), settings.TIME_ZONE)
        date_for_tomorrow_in_current_context = current_context_time + timezone.timedelta(days=1)
        start_time = make_datetime_timezone_aware_convert_to_utc(str(date_for_tomorrow_in_current_context.date())+" 00:00:00", "+0530")
        end_time = start_time + timezone.timedelta(hours=24)

        logger.info("Script:: PICKUP_SUMMARY:: start_time: %s - end_Time: %s" % (start_time, end_time))
        try:
            pickup_in_next_day_bookings = Booking.objects.select_related('user', 'usercar', 'usercar__car_model')\
                .filter(status_id__lt=9, pickup_time__range =[start_time, end_time])\
                .exclude(ops_status_id=8)

            pickup_data = []
            for booking in pickup_in_next_day_bookings:
                booking_packages = BookingPackage.objects.filter(booking=booking)
                package_taken = []
                panels = 0
                for item in booking_packages:
                    package_taken.append(item.package.package.name)
                    if item.package.package.category == Package.CATEGORY_DENT:
                        for panel_item in BookingPackagePanel.objects.filter(booking_package=item):
                            # Not using count here as full body will be counted as 14 panels.
                            panels += 1
                    if item.package.package.category == Package.CATEGORY_FULL_BODY:
                        panels += 14

                pickup_address = booking.booking_address.filter(type=BookingAddress.ADDRESS_TYPE_PICKUP).first()
                pickup_data.append({
                    'bookingId': booking.id,
                    'name': booking.user.name,
                    'phone': booking.user.phone,
                    'time': format_datetime_for_grid(booking.pickup_time),
                    'address': "%s, %s" % (pickup_address.address.address1, pickup_address.address.address2),
                    'packages': ', '.join(package_taken),
                    'panels': panels,
                    'car': str(booking.usercar.car_model),
                    'driver': booking.pickup_driver.name if booking.pickup_driver else '',
                })
            try:
                logger.info("Script:: PICKUP_SUMMARY:: pickup data: %s" % (pickup_data))
                notification = Notifications.objects.get(name='OPS_ALERT_PICKUP_FOR_TOMORROW')
                cc_address_list = notification.get_cc_list()
                to_address_list = notification.get_to_list()

                email_service = NewEmailService(to_address_list, cc_address_list, context={'pickup_data': pickup_data},
                                                analytic_info={'notification_id': notification.id})
                email_service.send(template_folder_name=notification.template_folder_name, subject=override_subject)

                logger.info("Script:: PICKUP_SUMMARY:: Sent")
            except:
                logger.exception("Script:: PICKUP_SUMMARY:: Failed")
        except:
            logger.exception("Script:: PICKUP_SUMMARY:: Failed to process to bookings")