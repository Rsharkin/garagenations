from push_notifications.models import GCMDevice, APNSDevice
from services.push_service import PushService
from core.constants import DEVICE_TYPE_ANDROID, DEVICE_TYPE_IOS
from core.models.message import Messages
from core.models.master import Notifications
import logging
logger = logging.getLogger(__name__)


def register_device_for_notification(user, registration_id, device_type=DEVICE_TYPE_ANDROID):
    """
        To register device.
    :param user:
    :param registration_id: GCM for android , APNS for IOS
    :param device_type: android/ios
    :return:
    """
    if device_type == DEVICE_TYPE_ANDROID:
        existing_devices = GCMDevice.objects.filter(user=user, registration_id=registration_id)
        if not existing_devices.exists():
            gcm_device = GCMDevice.objects.create(
                user=user,
                registration_id=registration_id
            )
            return gcm_device
        else:
            return existing_devices[0]
    elif device_type == DEVICE_TYPE_IOS:
        existing_devices = APNSDevice.objects.filter(user=user, registration_id=registration_id)
        if not existing_devices.exists():
            ios_device = APNSDevice.objects.create(
                user=user,
                registration_id=registration_id
            )
            return ios_device
        else:
            return existing_devices[0]


def request_location_of_user(users, sent_by_id):

    push_service = PushService(users)
    push_service.send_push_notice_to_users(message=None, extra_dict={
        'type': Messages.MESSAGE_TYPE_PUSH,
        'label': Notifications.LABEL_REQUEST_LOCATION
    }, analytic_info={
        'sent_by_id': sent_by_id,
    })


def send_notification(users, form_data, sent_by_id, notification_id=None):
    push_service = PushService(users)
    push_service.send_push_notice_to_users(form_data.get('message'), extra_dict={
        'type': form_data.get('notice_type'),
        'label': form_data.get('label'),
        'title': form_data.get('title'),
        'booking_id': form_data.get('booking_id'),
    }, analytic_info={
        'sent_by_id': sent_by_id,
        'notification_id': notification_id
    })


def send_notification_for_booking(send_to_user, booking, message, title, action_taken, notification_id=None, sent_by_id=None,
                                  extra_dict={}, notice_push_level=Messages.LABEL_STATUS):

    extra_dict['title'] = title
    extra_dict['ticker'] = ''

    extra_dict['type'] = 'app'
    extra_dict['booking_status'] = booking.status_id
    extra_dict['booking_id'] = booking.id
    extra_dict['label'] = notice_push_level

    analytic_info = {
        'action': action_taken,
        'notification_id': notification_id,
        'sent_by_id': sent_by_id,
    }

    if action_taken == 'SomeSpecialCondition':
        pass

    if not send_to_user:
        return False

    push_service = PushService(send_to_user)
    push_service.send_push_notice_to_users(message, extra_dict, analytic_info=analytic_info)