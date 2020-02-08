from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models.users import UserAuthCode
from core.models.master import Notifications
from core.models.message import Messages, MessageUser
from core.tasks import send_async_new_email_service
from core.utils import format_datetime_for_grid
import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    """
        Script to process system level alerts:
        1) Alert for OTP sent but not validated within x seconds.
    """
    can_import_settings = True
    help = 'Script:: OTP Failure processing'

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: OTP Failure processing:: Current_time: %s" % current_time)

        # Process OTP,
        # get all auth_request that are pending and for which alerts have not been processed.
        pending_auth_codes = UserAuthCode.objects.select_related('user').filter(system_alert_sent=False)

        logger.debug('Script:: OTP Failure processing:: Number of records to process=%s' % len(pending_auth_codes))
        try:
            # send alert for Otp that came in last x secs and are yet not validated
            for item in pending_auth_codes:
                # check whether diff b/w created_time and current time is more that x secs or not.
                time_since_requested = (current_time - item.created_at).seconds
                logger.debug('Script:: OTP Failure processing:: Time since requested=%s' % time_since_requested)
                if time_since_requested >= settings.WARNING_TIME_OTP_NOT_VALIDATED:
                    notices = Notifications.objects.filter(name='OTP_NOT_VALIDATED')
                    for notice in notices:
                        if notice.type == Notifications.NOTIFICATION_TYPE_EMAIL:
                            body = notice.template % {
                                'phone': item.user.phone if item.user.phone else '',
                                'otp': item.auth_code,
                                'otp_requested_at': format_datetime_for_grid(item.created_at),
                                'name': item.user.name if item.user.name else '',
                                'email': item.user.email if item.user.email else '',
                                'city': item.user.city.name if item.user.city else '',
                            }
                            logger.debug('Script:: OTP Failure processing:: Send Email for user_id=%s' % item.user.id)
                            send_async_new_email_service.delay(
                                to_list=notice.get_to_list(),
                                cc_list=notice.get_cc_list(),
                                subject=notice.subject,
                                body=body,
                                email_format='html',
                                message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS,
                                analytic_info={
                                    'notification_id': notice.id,
                                    'sent_for_account_id': item.user.id
                                }
                            )

                    item.system_alert_sent = True
                    item.save()
        except:
            logger.exception('Script:: OTP Failure processing:: Error while processing records ')

        # Remove expired auth_code
        expired_codes = pending_auth_codes.filter(expiry_dt__lte=current_time)
        if expired_codes:
            logger.debug('Script:: OTP Failure processing:: Deleting following expired auth_code = %s' % expired_codes)
            expired_codes.delete()
