"""
    Welcome Push Notification through localytics
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from core.models.users import UserDevices, UserInquiry
from core.models.booking import Booking
from requests.auth import HTTPBasicAuth
import requests
import uuid
import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = "Script:: CUSTOMER_WELCOME_PUSH:: Trigger push to customer for welcome through localytics"

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: CUSTOMER_WELCOME_PUSH:: Script started - current_time: %s" % current_time)
        two_hr_one_min_before = current_time - timedelta(hours=2, minutes=1)
        two_hr_before = current_time - timedelta(hours=2)
        # User devices added before 2 hours.
        user_devices = UserDevices.objects.filter(created_at__range=[two_hr_one_min_before, two_hr_before],
                                                  device_type='android',
                                                  is_active=True).select_related('user')
        try:
            logger.info("Script:: CUSTOMER_WELCOME_PUSH:: Starting welcome push notifications")
            extra = {
                "title": "Welcome to Bumper!",
                "message": "Save your time with *Free Pick Up & Drop* from anywhere in Bangalore. Book now!",
                "remarketing_type": "welcome",
                "dialog_image": "https://unbox-bumper.s3.amazonaws.com/31743393-502b-46d9-a081-0fd9508706a0.jpg",
                "creative_image": "https://unbox-bumper.s3.amazonaws.com/a3ffa495-0c97-43df-b057-ec4a7c75f519.jpg"
            }
            user_id_list = [{'user_id':user_device.user_id} for user_device in user_devices
                            if user_device.user.city_id in [1, None]]
            self.send_msg_to_localytics(user_id_list, common_extra=extra)
        except:
            logger.exception("Script:: CUSTOMER_WELCOME_PUSH:: Failed to process welcome notifications")

        try:
            logger.info("Script:: CUSTOMER_WELCOME_PUSH:: Starting a2c notifications")
            # Bookings in added to cart for user devices created exactly 2 hours before.
            # Bookings in added to cart for user devices created 2 hours before but cart added 10 min before.
            user_id_list = user_devices.values_list('user_id', flat=True)
            ten_min_before = current_time - timedelta(minutes=10)
            eleven_min_before = current_time - timedelta(minutes=11)
            a2c_user_list = Booking.objects.filter(
                                        (Q(status_id=1) & Q(updated_at__range=[ten_min_before,
                                                                               eleven_min_before]) &
                                         Q(user__userdevices__created_at__lt=two_hr_before) &
                                         Q(user__userdevices__device_type='android') &
                                         Q(user__userdevices__is_active=True)) |
                                        (Q(user_id__in=user_id_list) &
                                         Q(status_id=1))).select_related(
                                                                   'user',
                                                                   'usercar__car_model').values(
                                                                                         'user_id',
                                                                                         'user__name',
                                                                                         'usercar__car_model__name')
            already_added_user_ids = []
            final_a2c_list = []
            for a2c_user in a2c_user_list:
                if a2c_user.get('user_id') not in already_added_user_ids:
                    final_a2c_list.append(
                        {
                            'user_id': a2c_user.get('user_id'),
                            'extra': {
                                "title": "Did you forget something?",
                                "message": "Hey {user__name}, Looks like your car {usercar__car_model__name} "
                                           "is waiting in the cart, "
                                           "don't make her wait so long! Check your savings and schedule now!".format(
                                    **a2c_user),
                                "remarketing_type": "open_cart"
                            }
                        })
                    already_added_user_ids.append(a2c_user.get('user_id'))
            self.send_msg_to_localytics(final_a2c_list)
        except:
            logger.exception("Script:: CUSTOMER_WELCOME_PUSH:: Failed to process a2c notifications")

        # Bookings moved to added to cart 10 min before and user device created more than two hours before.
        try:
            logger.info("Script:: CUSTOMER_WELCOME_PUSH:: Starting userinquiry notifications")
            # Inquiry for user devices created exactly 2 hours before.
            # Inquiry for user devices created 2 hours before but cart added 10 min before.
            user_id_list = user_devices.values_list('user_id', flat=True)
            one_min_before = current_time - timedelta(minutes=1)
            ui_user_list = UserInquiry.objects.filter(
                                        (Q(updated_at__range=[one_min_before,
                                                              current_time]) &
                                         Q(user__userdevices__created_at__lt=two_hr_before) &
                                         Q(user__userdevices__device_type='android') &
                                         Q(user__userdevices__is_active=True)) |
                                        (Q(user_id__in=user_id_list))).select_related(
                                                                                'user').values(
                                                                                         'user_id',
                                                                                         'user__name')
            already_added_user_ids = []
            final_ui_list = []
            for ui_user in ui_user_list:
                if ui_user.get('user_id') not in already_added_user_ids:
                    final_ui_list.append(
                        {
                            'user_id': ui_user.get('user_id'),
                            'extra': {
                                "title": "Thanks for visiting Bumper!",
                                "message": "Hey {user__name}, thank you for inquiring with us. "
                                           "While our representatives get in touch with you, "
                                           "check out what our happy customers have to say about us!".format(**ui_user),
                                "url": "http://www.team-bhp.com/forum/bangalore/182872-body-repair-painting-detailing-bumper-com-bangalore.html",
                                "remarketing_type": "open_url"
                            }
                        })
                    already_added_user_ids.append(ui_user.get('user_id'))
            self.send_msg_to_localytics(final_ui_list)
        except:
            logger.exception("Script:: CUSTOMER_WELCOME_PUSH:: Failed to process userinquiry notifications")

    def send_msg_to_localytics(self, user_list, common_extra=None):
        app_id = "6da143188750090d39e18b1-2028c6c4-23ee-11e6-5a68-0042876ec363"
        # app_id="cb7d78068b3a8eef7776e44-a2880d00-78af-11e6-d3c4-001660e79be1"
        url = "https://messaging.localytics.com/v2/push/{}".format(app_id)
        key = "7538defbb583b2640de0dc2-af993e68-23ed-11e6-44b0-00adad38bc8d"
        secret = "6bf73d0bd5b9d46e5dc606d-af9941b0-23ed-11e6-44b0-00adad38bc8d"
        messages = [{
                        "target": str(obj.get('user_id')),
                        "alert": "",
                        "android": {
                            "extra": common_extra if common_extra else obj.get('extra')
                        }
                    } for obj in user_list]
        if messages:
            payload = {
                "request_id": str(uuid.uuid4()),
                "target_type": "customer_id",
                "campaign_key": "welcome_msg",
                "messages": messages
            }
            logger.info("Script:: CUSTOMER_WELCOME_PUSH:: Request payload to localytics - Payload: %s",
                        payload)
            r = requests.post(url, auth=HTTPBasicAuth(key, secret), json=payload)
            if r.status_code != 202:
                logger.error("Script:: CUSTOMER_WELCOME_PUSH:: Response from localytics - status_code: %s, output: %s",
                            r.status_code, r.json())
            else:
                logger.info("Script:: CUSTOMER_WELCOME_PUSH:: Response from localytics - status_code: %s, output: %s",
                            r.status_code, r.content)
        else:
            logger.info("Script:: CUSTOMER_WELCOME_PUSH:: No new devices to send to")
