"""
    temp script to send mail to all customers that signed up last week
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from services.email_service import NewEmailService
from core.models.users import BumperUser
from core.models.master import InternalAccounts
from core.models.booking import Booking

import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = "Script:: retarget_booking_completed:: Trigger email to customer for welcome"

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: retarget_booking_completed:: Script started - current_time: %s" % current_time)
        try:
            user_ids_to_send_to = set()
            bookings = Booking.objects.filter(city_id=1, user__email__isnull=False, status_id=23).exclude(
                user__email='')
            for ui in bookings:
                if InternalAccounts.objects.filter(phone=ui.user.phone).exclude(phone=8800165656).exists():
                    logger.info("Script:: retarget_booking_completed:: Skipping As Internal Account: %s", ui.user.id)
                    continue
                elif Booking.objects.filter(user=ui.user, return_reason__isnull=False).exists():
                    logger.info("Script:: retarget_booking_completed:: Skipping As booking returned: %s", ui.user.id)
                    continue
                else:
                    user_ids_to_send_to.add(ui.user.id)
            try:
                logger.info("Script:: retarget_booking_completed:: Sending mail to: %s", list(user_ids_to_send_to))
                users = BumperUser.objects.filter(id__in=list(user_ids_to_send_to))

                for user in users:
                    try:
                        email_service = NewEmailService([user.email], [],
                                                        context={'name': user.name},
                                                        analytic_info={'sent_for_account_id': user.id})

                        email_service.send(template_folder_name='retargetting-booking-completed')
                        pass
                    except:
                        logger.info("Script:: retarget_booking_completed:: Email send failure: %s", user.id)

                logger.info("Script:: retarget_booking_completed:: Processed")
            except:
                logger.exception("Script:: retarget_booking_completed:: Failed")
        except:
            logger.exception("Script:: retarget_booking_completed:: Failed to process to bookings")
