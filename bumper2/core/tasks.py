from __future__ import absolute_import
from djcelery import celery
import logging
from django.contrib.auth import get_user_model
User = get_user_model()
logger = logging.getLogger(__name__)
from core.models.booking import Booking


@celery.task
def upload_to_s3(booking_id, media_id):
    logger.debug('File to upload booking_id=%s media_id=%s' % (booking_id, media_id))
    from services.s3 import upload
    from core.models.common import Media
    from django.conf import settings

    row = Media.objects.filter(id=media_id, uploaded_to_s3=False).first()

    if row:
        upload(row.file, name=str(row.file),bucket_name=settings.BOTO_S3_BUCKET_BOOKING, prefix=str(booking_id))
        row.uploaded_to_s3 = True
        row.file = str(booking_id) + "/" + str(row.file)
        row.save()
    else:
        logger.error('File already in S3, booking_id=%s media_id=%s' % (booking_id, media_id))


# @celery.task
# def process_hooks(booking_id, old_status_id, new_status_id):
#     from core.managers.generalManager import process_hooks
#     process_hooks(booking_id, old_status_id, new_status_id)


# @celery.task
# def send_async_email(subject, body, to_list, cc_list, email_format='text'):
#     from services.email_service import NewEmailService
#     try:
#         email_service = NewEmailService(to_list=to_list, cc_list=cc_list, email_format=email_format)
#         email_service.send(email_body=body, subject=subject)
#     except:
#         logger.exception('Failed to send email.')


@celery.task
def send_async_sms(user_id, recipients, sms_text, analytic_info={}):
    from services.sms_service import SMSService
    from core.models.users import BumperUser
    try:
        user = None
        if user_id:
            user = BumperUser.objects.filter(id=user_id).first()
        sms_service = SMSService(user)
        logger.debug('Sending SMS to->%s' % recipients)
        for recipient in recipients:
            sms_service.send_sms(recipient, sms_text, analytic_info=analytic_info)
    except:
        logger.exception('Failed to send sms in sync mode.')

# TODO put mandril in place .. Do not delete this code.
# @celery.task
# def send_async_mandrill_email(to_email, template, var_list, template_content, bcc_list=None,subject=None):
#     from services.email_service import EmailService
#     EmailService.send_mail_using_mandrill(to_email, template, var_list=var_list, template_content=template_content,
#                                           bcc_list=bcc_list,subject=subject)


@celery.task
def send_async_new_email_service(to_list, cc_list=[], subject=None, body=None, template_folder_name=None,
                                 bcc_list=[], context={},email_format='text', analytic_info={}, message_direction=1):
    from services.email_service import NewEmailService
    email_service = NewEmailService(to_list, cc_list, bcc_list=bcc_list, context=context, email_format=email_format,
                                    analytic_info=analytic_info, message_direction=message_direction)
    email_service.send(email_body=body, subject=subject,template_folder_name=template_folder_name)


@celery.task
def process_hooks(booking_id, action_taken, extra_info_for_template={}, sent_by_id=None):
    from core.managers.generalManager import process_hooks
    process_hooks(booking_id, action_taken, extra_info_for_template, sent_by_id=sent_by_id)


@celery.task
def send_user_inquiry_to_ops(inquiry_id):
    from core.managers.generalManager import send_inquiry_to_ops
    from core.models.users import UserInquiry
    item = UserInquiry.objects.filter(id=inquiry_id).first()
    if item:
        send_inquiry_to_ops(item,item.inquiry)

# Commented as no longer used.
# @celery.task
# def send_inquiry_booking_to_ops(booking_id):
#     from core.models.booking import Booking
#     from core.managers.generalManager import send_inquiry_to_ops
#     booking = Booking.objects.filter(id=booking_id).first()
#     if booking:
#         send_inquiry_to_ops(booking,booking.desc)


@celery.task
def send_custom_notification_task(notif_name, template_vars, params_dict=None, user_id=None, message_direction=None):
    from core.models.users import BumperUser
    from core.managers.generalManager import send_custom_notification
    user = None
    if user_id:
        user = BumperUser.objects.get(id=user_id)
    send_custom_notification(notif_name, template_vars, params_dict=params_dict, user=user,
                             message_direction=message_direction)


@celery.task
def capture_razor_pay_payment(razor_payment_id, amount_in_paise, booking_id, bumper_payment_id):
    from core.utils import capture_razor_pay_payment
    capture_razor_pay_payment(razor_payment_id, amount_in_paise, booking_id, bumper_payment_id)


@celery.task
def update_booking_status_change_to_localytics(user_id, status_id, status_desc):
    from core.utils import update_booking_change_to_localytics
    from core.models.users import BumperUser
    user = BumperUser.objects.get(id=user_id)
    update_booking_change_to_localytics(user, status_id, status_desc)


@celery.task
def handle_car_pickup_incentive_task(booking_id):
    from core.utils import handle_car_pickup_incentive
    from core.models.booking import Booking
    booking = Booking.objects.filter(id=booking_id).first()
    handle_car_pickup_incentive(booking)


@celery.task
def handle_car_pickup_referral_task(booking_id):
    from core.utils import handle_car_pickup_referral
    from core.models.booking import Booking
    booking = Booking.objects.filter(id=booking_id).first()
    handle_car_pickup_referral(booking)


@celery.task
def update_event_respect_to_status_localytics(event_name, booking_id):
    logger.info("LOCALYTICS_EVENT:: update_localytics_event_celery_task with event_name: %s and booking id: %s "
                % (event_name, booking_id))
    try:
        booking_obj = Booking.objects.get(id=booking_id)
        if booking_obj:
            from core.utils import update_event_to_localytics
            attrs = {'booking_id': str(booking_id), 'status_id': str(booking_obj.status_id)}
            update_event_to_localytics(booking_obj.user, event_name, attrs)
    except Exception as e:
        logger.info('LOCALYTICS_EVENT:: The id which is passed inside the booking object does not exist')
        raise e


