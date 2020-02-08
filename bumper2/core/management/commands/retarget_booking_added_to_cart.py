"""
    Script to send mail to added to cart that were created in last 10 min and still not converted.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from services.email_service import NewEmailService
from core.models.booking import Booking
from core.models.message import Messages, MessageUser
from api.serializers.bookingSerializers import BookingSerializer
from core.models.master import Notifications

import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = "Script:: retarget_booking_added_to_cart:: Trigger email to customer for welcome"

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: retarget_booking_added_to_cart:: Script started - current_time: %s" % current_time)
        try:
            notification = Notifications.objects.get(id=154)
            booking_ids_to_send_to = set()
            bookings = Booking.objects.select_related('user').filter(user__email__isnull=False, status_id=1,
                                                                     created_at__lte=(current_time - timezone.timedelta(
                                                                         minutes=10))).exclude(user__email='')
            for booking in bookings:
                # this user does not have any completed booking.
                if not MessageUser.objects.filter(user=booking.user, message__notification=notification).exists():
                    booking_ids_to_send_to.add(booking.id)
            try:
                logger.info("Script:: retarget_booking_added_to_cart:: Sending mail to: %s", list(booking_ids_to_send_to))
                bookings = Booking.objects.select_related('user').filter(id__in=list(booking_ids_to_send_to))

                for booking in bookings:
                    try:
                        template_vars = {
                            'name': booking.user.name,
                            'booking_id': booking.id
                        }

                        booking_data = BookingSerializer(booking).data
                        template_vars['booking_data'] = booking_data
                        logger.info("Script:: retarget_booking_added_to_cart:: sending for: %s",
                                    booking.id)
                        new_service = NewEmailService(to_list=[booking.user.email],
                                                      cc_list=[], context=template_vars,
                                                      sender='shonalee@bumper.com',
                                                      from_name='Shonalee',
                                                      analytic_info={
                                                          'booking_id': booking.id,
                                                          'notification_id': notification.id,
                                                          'sent_for_account_id': booking.user.id,
                                                          'action': 1,
                                                          'sent_by_id': booking.user.id,
                                                          'label': Messages.LABEL_ADDED_TO_CART_RETARGET,
                                                      })
                        new_service.send(template_folder_name=notification.template_folder_name,
                                         attachments=[])
                    except:
                        logger.info("Script:: retarget_booking_added_to_cart:: Email send failure: %s", booking.id)

                logger.info("Script:: retarget_booking_added_to_cart:: Processed")
            except:
                logger.exception("Script:: retarget_booking_added_to_cart:: Failed")
        except:
            logger.exception("Script:: retarget_booking_added_to_cart:: Failed to process to bookings")
