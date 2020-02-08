import collections
from push_notifications.models import APNSDevice, GCMDevice
from core.models.message import (
    Messages,
    MessageUser,
)
import logging
log = logging.getLogger(__name__)


class PushService(object):
    """
        Class to hold the business logic for sending push notifications
        For now starting with sending based on Users selected.

        Things that can be set for Android GCM:
        registration_id, data, collapse_key=None, delay_while_idle=False, time_to_live=0

        Things that can be set for IOS:
        token, alert, badge=None, sound=None, category=None, content_available=False,
        action_loc_key=None, loc_key=None, loc_args=[], extra={}, identifier=0,
        expiration=None, priority=10, socket=None
    """
    message_send_level = Messages.MESSAGE_SEND_LEVEL_SPECIFIC
    message_direction = Messages.MESSAGE_DIRECTION_BUMPER_TO_CUSTOMER

    def __init__(self, users):
        self.users = users

    def send_push_notice_to_users(self, message=None, extra_dict={}, badge=None, analytic_info={}):
        """

        :param message: Message that will be shown in alert.
        :param extra_dict: extra params if needed to be sent.
        :param badge: For IOS only, number that is displayed in notification area.
        :return:
        """
        from core.models.users import UserDevices

        for k, v in extra_dict.items():
            extra_dict[k] = str(v) if str(v) != 'None' else ''
        message_to_save = message if message else str(extra_dict)

        # The first argument will be sent as "message" to the intent extras Bundle
        # Retrieve it with intent.getExtras().getString("message")

        # If you want to customize, send an extra dict and a None message.
        # the extras dict will be mapped into the intent extras Bundle.
        # For dicts where all values are keys this will be sent as url parameters,
        # but for more complex nested collections the extras dict will be sent via
        # the bulk message api.

        # Below check is put in place as there is difference between calling send_msg on Obj vs queryset.
        if isinstance(self.users, collections.Iterable):
            # For IOS/Apple Devices.
            ios_devices = APNSDevice.objects.filter(user__in=self.users, active=True)
            # For GCM/Android Devices.
            gcm_devices = GCMDevice.objects.filter(user__in=self.users, active=True)
            # For FCM devices
            user_devices = UserDevices.objects.filter(user__in=self.users, is_active=True, is_fcm=True)
        else:
            ios_devices = APNSDevice.objects.filter(user=self.users, active=True)
            gcm_devices = GCMDevice.objects.filter(user=self.users, active=True)
            user_devices = UserDevices.objects.filter(user=self.users, is_active=True, is_fcm=True)

        users_sent_gcm_message = list(gcm_devices.values_list('user', flat=True))
        users_sent_ios_message = list(ios_devices.values_list('user', flat=True))
        users_sent_fcm_message = list(user_devices.values_list('user', flat=True))

        users_sent_message = users_sent_fcm_message + users_sent_gcm_message + users_sent_ios_message

        if users_sent_message:
            message_obj = Messages.objects.create(
                message_type=Messages.MESSAGE_TYPE_PUSH,
                message=message_to_save,
                message_send_level=self.message_send_level,
                direction=self.message_direction,
                booking_id=extra_dict.get('booking_id'),
                label=extra_dict.get('label'),
                action=analytic_info.get('action'),
                notification_id=analytic_info.get('notification_id'),
                sent_by_id=analytic_info.get('sent_by_id'),
                subject=extra_dict.get('title'),
            )
            if len(users_sent_message) > 1:
                message_users = []
                already_processed_user_ids = []
                for user_id in users_sent_message:
                    if user_id not in already_processed_user_ids:
                        message_users.append(MessageUser(
                            user_id=user_id,
                            message=message_obj,
                        ))
                        already_processed_user_ids.append(user_id)

                if message_users:
                    MessageUser.objects.bulk_create(message_users)
            else:
                MessageUser.objects.create(user_id=users_sent_message[0], message=message_obj)

            extra_dict['id'] = str(message_obj.id)

            if user_devices:
                log.info('Sending FCM message to users=%s' % str(users_sent_fcm_message))
                click_action = None
                if extra_dict.get('booking_id'):
                    click_action = 'https://booking.bumper.com/core/bookings/editBooking/%s/' % extra_dict.get('booking_id')

                try:
                    user_devices.send_message(
                        title=extra_dict.get('title'),
                        body=message,
                        icon=None,
                        data=extra_dict,
                        click_action=click_action,
                        sound="default" if message else None,
                        # badge="+1",
                    )
                except:
                    log.exception('Failed to send push notification to fcm devices.')
                    raise
            else:
                log.debug('There is no active FCM device for these users: %s' % self.users)

            if gcm_devices:
                try:
                    if len(gcm_devices) > 1:
                        gcm_devices.send_message(message, extra=extra_dict)
                    else:
                        gcm_devices[0].send_message(message, extra=extra_dict)

                    log.debug('User=%s, GCM Devices message sent to = %s' % (self.users, len(gcm_devices)))
                except:
                    log.exception('Failed to send push notification to GCM devices. %s' % list(gcm_devices.values_list('id', flat=True)))
                    raise
            else:
                log.debug('There is no active GCM device for these users: %s' % self.users)

            if ios_devices:
                if len(ios_devices) > 1:
                    # send using bulk messages.
                    ios_devices.send_message(message, sound='default', badge="+1", extra=extra_dict)
                else:
                    ios_devices[0].send_message(message, sound='default', badge="+1", extra=extra_dict)

                log.debug('User=%s, IOS Devices message sent to = %s' % (self.users, len(ios_devices)))
                for device in ios_devices:
                    log.debug('Sent To=%s' % device.registration_id)
            else:
                log.debug('There is no active IOS device for these users: %s' % self.users)

            # Other examples if need in future.
            # device.send_message("You've got mail") # Alert message may only be sent as text.
            # device.send_message(None, badge=5) # No alerts but with badge.
            # device.send_message(None, badge=1, extra=extra_dict) # Silent message with badge and added custom data.