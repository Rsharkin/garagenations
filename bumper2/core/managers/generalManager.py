from django.utils import timezone
from django.conf import settings
from services.sms_service import SMSService
from core.utils import pdf
from services.email_service import NewEmailService, EmailService
import logging
import base64
import requests
from core.utils import format_datetime_for_grid, format_datetime_for_msg, format_date_for_grid
logger = logging.getLogger(__name__)


def process_sms_delivery_callback(data):
    from core.models.message import MessageUser
    message_id = data.get('msgid')
    message_users = MessageUser.objects.filter(id=message_id)
    if not message_users:
        logger.error('No Message for this SMS Callback!!')
    else:
        message_user = message_users.first()
        message_user.delivery_report = data.get('status')
        message_user.delivered_dt = timezone.now()
        message_user.save()


def process_hooks(booking_id, action_taken, extra_info_for_template={}, sent_by_id=None, notice_for='flow'):
    """

    :param booking_id:
    :param action_taken:
    :param notice_for: options flow/eod
    :return:
    """
    logger.debug('Processing hook for booking_id=%s' % str(booking_id))

    from core.models.booking import Booking, BookingPackage, BookingAddress
    from core.models.master import Hooks, Notifications
    from core.models.message import Messages
    from core.managers.bookingManager import get_bill_details_new
    from api.custom_auth import get_booking_token
    from core.managers.pushNotificationManager import send_notification_for_booking
    from core.managers.userManager import get_user_active_devices
    from core.models.users import NotificationSubscriber
    from api.serializers.bookingSerializers import BookingSerializer

    booking = Booking.objects.select_related('user', 'usercar', 'usercar__car_model').get(id=booking_id)
    hooks = Hooks.objects.select_related('notification').filter(action_taken=action_taken,
                                                                notification__notice_for=notice_for)

    # TODO Refine this code.

    bill_amt = ''
    payable_amt = ''
    attachment = {}
    booking_token = get_booking_token(booking)
    app_redirect_link =get_short_url(settings.BUMPER_APP_URL_THROUGH_APP_REDIRECT_URL % str(booking_id))
    direct_payment_url =get_short_url(settings.DIRECT_PAYMENT_URL_BASE % booking_token)
    payment_url = get_short_url(settings.PAYMENT_URL % str(booking_id))
    bill_details = get_bill_details_new(booking)
    if bill_details and bill_details.get('total_amt'):
        bill_amt = bill_details.get('total_amt')

    if bill_details and bill_details.get('payable_amt'):
        payable_amt = bill_details.get('payable_amt')

    booking_packages = BookingPackage.objects.filter(booking=booking)
    package_taken = []
    for item in booking_packages:
        package_taken.append(item.package.package.name)

    pickup_time = format_datetime_for_grid(booking.pickup_time)
    if pickup_time and format_datetime_for_grid(booking.pickup_slot_end_time):
        pickup_time = pickup_time + ' - ' + format_datetime_for_msg(booking.pickup_slot_end_time)

    customer_eta_dt = format_date_for_grid(booking.estimate_complete_time)
    customer_eta_datetime = format_datetime_for_grid(booking.estimate_complete_time)

    pickup_address = booking.booking_address.filter(type=BookingAddress.ADDRESS_TYPE_PICKUP).first()
    drop_address = booking.booking_address.filter(type=BookingAddress.ADDRESS_TYPE_DROP).first()
    user_has_app = False

    if get_user_active_devices(booking.user):
        user_has_app = True

    template_vars = {
        'booking_id': booking_id,
        'city': booking.city.name if booking.city else '',
        'car_model': booking.usercar.car_model,
        'car_reg_no':booking.usercar.registration_number if booking.usercar.registration_number else '',
        'pickup_driver_name': booking.pickup_driver.name if booking.pickup_driver else '',
        'pickup_driver_phone': booking.pickup_driver.ops_phone if booking.pickup_driver else '',
        'drop_driver_name': booking.drop_driver.name if booking.drop_driver else '',
        'drop_driver_phone': booking.drop_driver.ops_phone if booking.drop_driver else '',
        'cc_num': settings.BUMPER_SUPPORT_NUM,  # customer care bumper
        'cc_email': settings.BUMPER_SUPPORT_EMAIL,  # customer care bumper
        'bill_amount': bill_amt,
        'payable_amt': payable_amt,
        'package_list': booking_packages,
        'package_details': ', '.join(package_taken),
        'pickup_details': pickup_time if pickup_time else '',
        'customer_name': booking.user.name,
        'customer_phone': booking.user.phone,
        'current_status': booking.status.status_desc if booking.status else '',
        'current_ops_status': booking.ops_status.ops_status_desc if booking.ops_status else '',
        'pickup_address': "%s %s %s %s" % (pickup_address.address.address1, pickup_address.address.address2 if pickup_address.address.address2 else '', pickup_address.address.city if pickup_address.address.city else '', pickup_address.address.pin_code if pickup_address.address.pin_code else '') if pickup_address else '',
        'user_has_app': user_has_app,
        'amt_paid': extra_info_for_template.get('amt_paid'),
        'app_redirect_url':app_redirect_link ,
        'utm_source': booking.user.utm_source if booking.user.utm_source else '',
        'utm_medium': booking.user.utm_medium if booking.user.utm_medium else '',
        'utm_campaign': booking.user.utm_campaign if booking.user.utm_campaign else '',
        'user_source': booking.user.source if booking.user.source else '',
        'booking_source': booking.source if booking.source else '',
        'delivery_datetime': customer_eta_datetime,
        'delivery_dt': customer_eta_dt,
        "payment_link": payment_url,
        "direct_payment_link": direct_payment_url,
        "feedback_link":settings.FEEDBACK_BASE_URL % booking_token,
        "base_url":settings.BASE_URL_WEB,
        "booking_token": booking_token,
    }
    for hook in hooks:
        try:
            logger.debug('Processing hook for booking_id=%s hook_id=%s' % (booking_id, hook.id))
            if hook.notification.type == Notifications.NOTIFICATION_TYPE_EMAIL:
                booking_data = BookingSerializer(booking).data
                template_vars['booking_data'] = booking_data

                to_list = hook.notification.get_to_list()
                cc_list = hook.notification.get_cc_list()
                if hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_CUSTOMER:
                    to_list = [booking.user.email]
                    cc_list = []

                new_service = NewEmailService(to_list=to_list,
                                              cc_list=cc_list, context=template_vars,
                                              analytic_info={
                                                  'booking_id': booking.id,
                                                  'notification_id': hook.notification.id,
                                                  'sent_for_account_id': booking.user.id,
                                                  'action': action_taken,
                                                  'sent_by_id': sent_by_id,
                                                  'label': Messages.LABEL_EOD if notice_for == Notifications.NOTICE_FOR_EOD else None,
                                              })
                if action_taken == 16:
                    attachment = {
                        'content': base64.b64encode(pdf('invoice.html', template_vars).read()),
                        'name': 'invoice_pdf',
                        'type': 'application/pdf'
                    }

                if hook.notification.use_file_template:
                    new_service.send(template_folder_name=hook.notification.template_folder_name, attachments=[attachment])
                else:
                    new_service.send(email_body=hook.notification.template, subject=hook.notification.subject)

            elif hook.notification.type == Notifications.NOTIFICATION_TYPE_SMS:

                sms_service = SMSService(booking.user, is_promo=hook.notification.is_promo)
                sms_text = hook.notification.template
                try:
                    sms_text = sms_text % template_vars
                    send_to_phone = None
                    if hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_CUSTOMER:
                        send_to_phone = booking.user.phone
                    elif hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_OPS:
                        send_to_phone = hook.notification.to
                    elif hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_PICKUP_DRIVER:
                        send_to_phone = booking.pickup_driver.ops_phone if booking.pickup_driver else None
                    elif hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_DROP_DRIVER:
                        send_to_phone = booking.drop_driver.ops_phone if booking.drop_driver else None
                    elif hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_WORKSHOP_EXECUTIVE:
                        send_to_phone = booking.workshop_executive.ops_phone if booking.workshop_executive else None

                    if send_to_phone:
                        analytic_info = {
                            'action': action_taken,
                            'notification_id': hook.notification.id,
                            'sent_by_id': sent_by_id,
                            'booking_id': booking.id,
                            'label': Messages.LABEL_EOD if notice_for == Notifications.NOTICE_FOR_EOD else None,
                        }
                        logger.info('Sending SMS to=%s content=%s' % (send_to_phone, sms_text))
                        sms_service.send_sms(send_to_phone, sms_text, analytic_info=analytic_info)
                except KeyError:
                    logger.exception('SMS template using variable that is not in data. template=%s' % sms_text)

            elif hook.notification.type == Notifications.NOTIFICATION_TYPE_PUSH:
                body = hook.notification.template
                subject = hook.notification.subject
                try:
                    body = body % template_vars
                    subject = subject % template_vars
                    send_to_user = []
                    if hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_CUSTOMER:
                        send_to_user = [booking.user]
                    elif hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_PICKUP_DRIVER:
                        send_to_user = [booking.pickup_driver]
                    elif hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_DROP_DRIVER:
                        send_to_user = [booking.drop_driver]
                    elif hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_WORKSHOP_EXECUTIVE:
                        from core.models.users import WorkshopUser
                        list_of_users = []
                        for item in WorkshopUser.objects.filter(workshop=booking.workshop,
                                                                role=WorkshopUser.ROLE_BUMPER_EXECUTIVE):
                            list_of_users.append(item.user)
                        send_to_user = list_of_users
                    elif hook.notification.send_notice_to == Notifications.SEND_NOTICE_TO_OPS:
                        notification_subscribers = NotificationSubscriber.objects.filter(notification=hook.notification)
                        for item in notification_subscribers:
                            send_to_user.append(item.user)

                    if send_to_user:
                        send_notification_for_booking(send_to_user, booking, body, subject, action_taken,
                                                      notification_id=hook.notification.id, sent_by_id=sent_by_id,
                                                      notice_push_level=hook.notification.push_level)
                except KeyError:
                    logger.exception('Push notice template using variable that is not in data. template=%s' % body)
        except:
            logger.exception('Failed to Process Hook=%s' % hook)


def send_inquiry_to_ops(item,message):
    from core.models.master import Notifications
    from core.models.message import Messages
    notices = Notifications.objects.filter(name='OPS_MESSAGE_FROM_CUSTOMER')
    for notice in notices:
        if notice.type == Notifications.NOTIFICATION_TYPE_EMAIL:
            context = {
               'name': item.user.name if item.user.name else '',
               'email': item.user.email if item.user.email else '',
               'mobile': item.user.phone if item.user.phone else '',
               'city': item.city.name if item.city else '',
               'message': message,
               'utm_source': item.user.utm_source if item.user.utm_source else '',
               'utm_medium': item.user.utm_medium if item.user.utm_medium else '',
               'utm_campaign': item.user.utm_campaign if item.user.utm_campaign else '',
               'source': item.source.source_desc if item.source else '',
            }
            # body = notice.template % context
            # subject = notice.subject % context

            logger.debug('Send Email for inquiry id=%s' % item.id)
            from services.email_service import NewEmailService
            email_service = NewEmailService(
                to_list=notice.get_to_list(),
                cc_list=notice.get_cc_list(),
                email_format='html',
                context=context,
                message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS,
                analytic_info={
                   'notification_id': notice.id,
                   'sent_for_account_id': item.user.id
                }
            )

            email_service.send(email_body=notice.template, subject=notice.subject)


def send_custom_notification(notif_name, template_vars, params_dict=None, user=None,
                             message_direction=None, attachments=None):
    """
    Send Notification in general.
    :param notif_name: This is the notification name from the Notification Table.
    :param template_vars: This is the parameters dictionary required for populating subject and body.
    :param params_dict: This is the parameters dictionary required for analytic info or any other information.
    :param user: Optional: This is required only if notification is for user.
    :return:

    NOTE: This is only being tested for Email notification. For others use after testing.
    """
    from core.models.master import Notifications
    from core.models.message import Messages
    from core.models.users import NotificationSubscriber

    try:
        if not params_dict:
            params_dict = {}

        logger.debug('Processing Notification notif_name=%s params_dict=%s' % (notif_name, params_dict))
        notices = Notifications.objects.filter(name=notif_name)
        for notification in notices:
            if notification.type == Notifications.NOTIFICATION_TYPE_EMAIL:
                to_list = notification.get_to_list()
                cc_list = notification.get_cc_list()
                if notification.send_notice_to == Notifications.SEND_NOTICE_TO_CUSTOMER:
                    to_list = [user.email]
                    cc_list = []

                new_service = NewEmailService(to_list=to_list,
                                              cc_list=cc_list, context=template_vars,
                                              message_direction=message_direction,
                                              analytic_info={
                                                  'booking_id': params_dict.get('booking_id'),
                                                  'notification_id': notification.id,
                                                  'action': params_dict.get('action'),
                                                  'sent_for_account_id': params_dict.get('sent_for_account_id'),
                                                  'sent_by_id': params_dict.get('sent_by_id'),
                                              })
                if notification.use_file_template:
                    new_service.send(template_folder_name=notification.template_folder_name)
                else:
                    new_service.send(email_body=notification.template, subject=notification.subject,
                                     attachments=attachments)

            elif notification.type == Notifications.NOTIFICATION_TYPE_SMS:
                # This is only for User for now. Will be modified when required to send SMS to ops team as well.
                sms_service = SMSService(user, is_promo=notification.is_promo)
                sms_text = notification.template
                try:
                    sms_text = sms_text % template_vars
                    if notification.send_notice_to in [Notifications.SEND_NOTICE_TO_CUSTOMER,
                                                       Notifications.SEND_NOTICE_TO_CUSTOM] :
                        analytic_info = {
                            'action': params_dict.get('action'),
                            'notification_id': notification.id,
                            'sent_by_id': params_dict.get('sent_by_id'),
                            'booking_id': params_dict.get('booking_id'),
                        }
                        recipient = params_dict.get('phone')
                        if user and user.phone:
                            recipient = user.phone
                        if recipient:
                            logger.info('Sending SMS to=%s content=%s' % (recipient, sms_text))
                            sms_service.send_sms(recipient, sms_text, analytic_info=analytic_info)
                        else:
                            logger.error('Sending SMS failed because no recipient, content=%s' % sms_text)
                except KeyError:
                    logger.exception('SMS template using variable that is not in data. template=%s' % sms_text)

            elif notification.type == Notifications.NOTIFICATION_TYPE_PUSH:
                body = notification.template
                subject = notification.subject
                try:
                    from pushNotificationManager import send_notification
                    body = body % template_vars
                    subject = subject % template_vars
                    push_data = {
                        'message': body,
                        'notice_type': 'app',
                        'label': notification.push_level,
                        'title': subject,
                        'booking_id': params_dict.get('booking_id'),
                    }

                    send_to_user = [user]
                    if notification.send_notice_to == Notifications.SEND_NOTICE_TO_OPS:
                        notification_subscribers = NotificationSubscriber.objects.filter(notification=notification)
                        for item in notification_subscribers:
                            send_to_user.append(item.user)

                    send_notification(send_to_user, push_data, sent_by_id=params_dict.get('sent_by_id'),
                                      notification_id=notification.id)
                except KeyError:
                    logger.exception('Push notice template using variable that is not in data. template=%s' % body)
    except:
        logger.exception('Failed to Process Notification.')


def save_manually_sent_eod_message(booking, message_details, sent_by_id):
    from core.models.message import Messages, MessageUser
    message_obj = Messages.objects.create(
        message_type=message_details.get('message_type', Messages.MESSAGE_TYPE_SMS),
        message=message_details.get('message','EOD update'),
        message_send_level=Messages.MESSAGE_SEND_LEVEL_SPECIFIC,
        direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_CUSTOMER,
        booking_id=booking.id,
        action=message_details.get('action'),
        sent_by_id=sent_by_id,
    )
    message_user = MessageUser.objects.create(user_id=booking.user.id, message=message_obj)


def send_quick_pickup_notice_to_ops(booking_id):
    """
        Function added to send notifications to ops team for quick pickup.
    :return:
    """
    from core.tasks import send_async_sms
    from core.models.booking import Booking
    from core.models.master import Notifications

    sms_notice = Notifications.objects.get(name='OPS_SMS_QUICK_PICKUP_SCHEDULED')
    number_to_send_to = settings.ALERT_QUICK_PICKUP

    booking = Booking.objects.get(id=booking_id)
    pickup_time = format_datetime_for_grid(booking.pickup_time)
    if pickup_time and format_datetime_for_grid(booking.pickup_slot_end_time):
        pickup_time = pickup_time + ' - ' + format_datetime_for_msg(booking.pickup_slot_end_time)

    sms_text = sms_notice.template % ({
        'booking_id': booking.id,
        'city': booking.city.name if booking.city else '',
        'car_model': booking.usercar.car_model.name,
        'pickup_details': pickup_time
    })
    logger.debug('Text for pickup_time->%s, converted=%s' % (booking.pickup_time, timezone.localtime(booking.pickup_time)))
    send_async_sms(booking.user_id, number_to_send_to, sms_text)


def get_short_url(long_url):
    url = "https://www.googleapis.com/urlshortener/v1/url?key={}".format(settings.SHORT_URL_API_KEY)
    data = {"longUrl": long_url}
    headers = {'content-type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        output = response.json()
        return output.get('id')
    else:
        logger.error("Error getting short url of (%s), error: %s", long_url, response.json())
        return None
