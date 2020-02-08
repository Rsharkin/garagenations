"""
    temp script to send mail to all customers that signed up last week
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from services.email_service import NewEmailService
from core.models.master import InternalAccounts
from core.models.users import BumperUser, UserInquiry
from core.models.booking import Booking
from core.models.message import Messages
from services.push_service import PushService

import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = "Script:: retarget_booking_open:: Retargeting email"

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: retarget_booking_open:: Script started - current_time: %s" % current_time)
        try:
            user_ids_to_send_to = set()
            users_to_consider = list(Booking.objects.values_list('user', flat=True).filter(city_id=1,
                                                                                       user__email__isnull=False,
                                                                                       user__date_joined__gt=current_time - timezone.timedelta(
                                                                                           weeks=2),
                                                                                       status_id=1).exclude(
                user__email=''))

            users_to_consider += list(UserInquiry.objects.values_list('user', flat=True).filter(city_id=1,
                                                                                            user__email__isnull=False,
                                                                                            user__date_joined__gt=current_time - timezone.timedelta(
                                                                                                weeks=2),
                                                                                            status__in=[1, 2, 3,
                                                                                                        5]).exclude(
                user__email=''))

            users = BumperUser.objects.filter(id__in=users_to_consider)

            for u in users:
                if InternalAccounts.objects.filter(phone=u.phone).exclude(phone=8800165656).exists():
                    logger.info("Script:: retarget_booking_open:: Skipping As Internal Account: %s", u.id)
                    continue
                elif Booking.objects.filter(user=u, status_id__gte=3, status_id__lte=23).exists():
                    logger.info("Script:: retarget_booking_open:: Skipping As active booking there: %s", u.id)
                    continue
                else:
                    user_ids_to_send_to.add(u.id)
            try:
                logger.info("Script:: retarget_booking_open:: Sending mail to: %s - %s" % (len(list(user_ids_to_send_to)), list(user_ids_to_send_to)))
                send_to_users = BumperUser.objects.filter(id__in=list(user_ids_to_send_to))

                for user in send_to_users:
                    try:
                        email_service = NewEmailService([user.email], [],
                                                        context={'name': user.name},
                                                        analytic_info={'sent_for_account_id': user.id})

                        email_service.send(template_folder_name='retargetting-gst-change')
                    except:
                        logger.info("Script:: retarget_booking_open:: Email send failure: %s", user.id)

                extra_dict={}
                extra_dict['title'] = "Get your car repaired before 28th Aug to avoid GST price rise by 18%"
                extra_dict['ticker'] = ''

                extra_dict['type'] = 'app'
                extra_dict['label'] = Messages.LABEL_OFFER

                analytic_info = {
                }

                push_service = PushService(send_to_users)
                push_service.send_push_notice_to_users("We're adjusting our price from tomorrow, 25th Aug. But you can avail our services at the existing price if you get your car repaired before 28th August. *Exclusively for you*.", extra_dict, analytic_info=analytic_info)
                logger.info("Script:: retarget_booking_open:: Processed")
            except:
                logger.exception("Script:: retarget_booking_open:: Failed")
        except:
            logger.exception("Script:: retarget_booking_open:: Failed to process to bookings")
