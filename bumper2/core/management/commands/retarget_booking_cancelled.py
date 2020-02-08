"""
    temp script to send mail to all customers that signed up last week
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from services.email_service import NewEmailService
from time import sleep
from core.models.users import BumperUser
from core.models.booking import Booking
from core.models.message import Messages, MessageUser

import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = "Script:: retarget_booking_cancelled:: Trigger email to customer for welcome"

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: retarget_booking_cancelled:: Script started - current_time: %s" % current_time)
        try:
            user_ids_to_send_to = set()
            bookings = Booking.objects.filter(city_id=1, user__email__isnull=False, status_id=24,
                                              ops_status_id=28,
                                              created_at__gt=(current_time-timezone.timedelta(days=180))).exclude(user__email='')
            for ui in bookings:
                # this user does not have any completed booking.
                if MessageUser.objects.filter(user=ui.user, message__subject="Repair your car now before you will have to replace\n").exists():
                    logger.info("Script:: retarget_booking_cancelled:: Skipping yesterday's mistake : %s", ui.user.id)
                    continue
                elif Booking.objects.filter(status_id__gte=9, user=ui.user, return_reason__isnull=True).exclude(
                        status_id=24).exists():
                    logger.info("Script:: retarget_booking_cancelled:: Skipping user as booking converted: %s", ui.user.id)
                    continue
                else:
                    user_ids_to_send_to.add(ui.user.id)
            try:
                logger.info("Script:: retarget_booking_cancelled:: Sending mail to: %s", list(user_ids_to_send_to))
                users = BumperUser.objects.filter(id__in=list(user_ids_to_send_to))

                for user in users:
                    try:
                        email_service = NewEmailService([user.email], [],
                                                        context={'name': user.name},
                                                        analytic_info={'sent_for_account_id': user.id})

                        email_service.send(template_folder_name='retargetting-booking-cancelled')
                        sleep(0.100)
                    except:
                        logger.info("Script:: retarget_booking_cancelled:: Email send failure: %s", user.id)

                logger.info("Script:: retarget_booking_cancelled:: Processed")
            except:
                logger.exception("Script:: retarget_booking_cancelled:: Failed")
        except:
            logger.exception("Script:: retarget_booking_cancelled:: Failed to process to bookings")
