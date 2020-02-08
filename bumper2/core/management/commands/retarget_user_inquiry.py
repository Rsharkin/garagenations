"""
    temp script to send mail to all customers that signed up last week
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from services.email_service import NewEmailService
from time import sleep
from core.models.users import BumperUser, UserInquiry
from core.models.booking import Booking

import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = "Script:: retarget_user_inquiry:: Trigger email to customer for welcome"

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: retarget_user_inquiry:: Script started - current_time: %s" % current_time)
        try:
            user_ids_to_send_to = set()
            user_inquiries = UserInquiry.objects.filter(city_id=1, user__email__isnull=False,
                                                        status__in=[6, 7, 10, 11]).exclude(user__email='')
            for ui in user_inquiries:
                # this user does not have any completed booking.
                if Booking.objects.filter(status_id__gte=9, user=ui.user, return_reason__isnull=True).exclude(
                        status_id=24).exists():
                    logger.info("Script:: retarget_user_inquiry:: Skipping user as booking converted: %s", ui.user.id)
                    continue
                else:
                    user_ids_to_send_to.add(ui.user.id)
            try:
                logger.info("Script:: retarget_user_inquiry:: Sending mail to: %s", list(user_ids_to_send_to))
                users = BumperUser.objects.filter(id__in=list(user_ids_to_send_to))

                for user in users:
                    try:
                        email_service = NewEmailService([user.email], [],
                                                        context={'name': user.name},
                                                        analytic_info={'sent_for_account_id': user.id})

                        email_service.send(template_folder_name='retargetting-inquiry-booking-cancelled')
                        sleep(0.100)
                        logger.info("Script:: retarget_user_inquiry:: Processed :%s", user.id)
                    except:
                        logger.info("Script:: retarget_user_inquiry:: Email send failure: %s", user.id)
            except:
                logger.exception("Script:: retarget_user_inquiry:: Failed")
        except:
            logger.exception("Script:: retarget_user_inquiry:: Failed to process to bookings")
