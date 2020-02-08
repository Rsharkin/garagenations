import pytz
import datetime
from django.utils import timezone
from django.conf import settings
from django.db.models import Count
from dateutil import parser
import uuid
import hmac
from django.forms.models import model_to_dict
from core import constants
import logging
from django.db import connection
from django.shortcuts import HttpResponse
from bs4 import BeautifulSoup
import ujson
import requests
import re
import time
from requests.auth import HTTPBasicAuth
from django.template.loader import render_to_string
from weasyprint import HTML
logger = logging.getLogger(__name__)
try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha


def generate_api_key():
    # Get a random UUID.
    new_uuid = uuid.uuid4()
    # Hmac that beast.
    return hmac.new(new_uuid.bytes, digestmod=sha1).hexdigest()


def generate_sms_auth_code():
    import random
    # four digit random number
    return random.randint(1000, 9999)


def _convert_to_given_timezone(dtObj, tz_name):
    tzone = pytz.timezone(tz_name)
    return dtObj.astimezone(tzone)


def _convert_naive_datetime_to_given_timezone(dtObj, tz_name='UTC'):
    datetime_obj_utc = dtObj.replace(tzinfo=pytz.timezone(tz_name))
    return datetime_obj_utc


def make_datetime_timezone_aware_convert_to_utc(dt, tz_name):
    """
        make datetime timezone aware.
        dt like 2014-06-01 00:00:00
        tz like +0530
    """
    if tz_name and dt:
        return _convert_to_given_timezone(parser.parse(str(dt) + str(tz_name)), 'UTC')


def make_date_utc_timezone_aware(dt, tz_offset):
    datetime_with_start_time = timezone.datetime(dt.year, dt.month, dt.day)
    start = parser.parse(str(datetime_with_start_time) + str(tz_offset))
    return _convert_to_given_timezone(start, 'UTC')


def get_time_till_now_in_min(dt1):
    now = timezone.now()
    return divmod((now - dt1).total_seconds(), 60)[0]


def current_time_user_timezone():
    return _convert_to_given_timezone(timezone.now(), settings.TIME_ZONE)


def format_datetime_for_grid(dt):
    if dt:
        aware_timezone = _convert_naive_datetime_to_given_timezone(dt)
        return datetime.datetime.strftime(_convert_to_given_timezone(aware_timezone, settings.TIME_ZONE),
                                          "%d %b %H:%M")
    else:
        return None


def format_date_for_grid(dt):
    if dt:
        aware_timezone = _convert_naive_datetime_to_given_timezone(dt)
        return datetime.datetime.strftime(_convert_to_given_timezone(aware_timezone, settings.TIME_ZONE),
                                          "%d-%b")
    else:
        return None


def format_datetime_for_msg(dt):
    if dt:
        aware_timezone = _convert_naive_datetime_to_given_timezone(dt)
        return datetime.datetime.strftime(_convert_to_given_timezone(aware_timezone, settings.TIME_ZONE),
                                          "%H:%M")
    else:
        return None


def format_datetime_for_form(dt):
    if dt:
        aware_timezone = _convert_naive_datetime_to_given_timezone(dt)
        return datetime.datetime.strftime(_convert_to_given_timezone(aware_timezone, settings.TIME_ZONE),
                                          "%Y-%m-%d %H:%M")
    else:
        return None


def get_start_and_end_dt_by_dur_type(duration_type, start_dt, end_dt):
    import calendar

    start_time = None
    end_time = None
    today = timezone.now()
    if duration_type == constants.DURATION_RANGE:
        start_time = start_dt
        end_time = end_dt

    elif duration_type == constants.DURATION_TODAY:
        start_time = today
        end_time = today

    elif duration_type == constants.DURATION_THIS_WEEK:
        start_time = today - timezone.timedelta(today.weekday())
        end_time = start_time + timezone.timedelta(6)

    elif duration_type == constants.DURATION_LAST_WEEK:
        end_time = today - timezone.timedelta(today.weekday() + 1)
        start_time = end_time - timezone.timedelta(6)

    elif duration_type == constants.DURATION_THIS_MONTH:
        days_in_month = calendar.monthrange(today.year, today.month)[1]  # return tuple (1, 31)
        start_time = today - timezone.timedelta(today.day - 1)
        end_time = start_time + timezone.timedelta(days_in_month - 1)

    elif duration_type == constants.DURATION_LAST_MONTH:
        cur_month = today.month
        if cur_month == 1:
            last_month = 12
        else:
            last_month = cur_month - 1
        days_in_month = calendar.monthrange(today.year, last_month)[1]  # return tuple (1, 31)
        end_time = today - timezone.timedelta(today.day)
        start_time = end_time - timezone.timedelta(days_in_month - 1)

    start_time = _convert_to_given_timezone(
        _convert_naive_datetime_to_given_timezone(timezone.datetime.combine(start_time, datetime.time.min)),
        settings.TIME_ZONE)
    end_time = _convert_to_given_timezone(
        _convert_naive_datetime_to_given_timezone(timezone.datetime.combine(end_time, datetime.time.max)),
        settings.TIME_ZONE)

    return start_time, end_time


def convert_model_to_dict_for_form(instance):
    """
        Function to create model to dict with datetime fields having autonow= True
        Also to format datetime field to proper string values that can be used in grid.
    :param mod:
    :return:
    :addedBy: Inderjeet
    """
    from datetime import datetime
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields:
        if isinstance(f.value_from_object(instance), datetime):
            data[f.name] = format_datetime_for_form(f.value_from_object(instance))
        else:
            data[f.name] = f.value_from_object(instance)
    return data


def convert_model_to_dict(model_list):
    """
        Function to create model to dict with datetime fields having autonow= True
    :param mod:
    :return:
    """
    item_list = []
    for item in model_list:
        model_dict = model_to_dict(item)
        model_dict['updated_at'] = format_datetime_for_form(item.updated_at)
        model_dict['created_at'] = format_datetime_for_form(item.created_at)
        item_list.append(model_dict)

    return item_list


def single_model_to_dict(item):
    model_dict = model_to_dict(item)
    model_dict['updated_at'] = item.updated_at
    model_dict['created_at'] = item.created_at
    return model_dict


def build_s3_path(file_name, bucket_name=None):
    from services.settings import BOTO_S3_BUCKET
    if not bucket_name:
        bucket_name = BOTO_S3_BUCKET
    return "https://%s.s3.amazonaws.com/%s" % (bucket_name, file_name)


def build_s3_folder_path(file_name, folder_name, bucket_name=None):
    from services.settings import BOTO_S3_BUCKET
    if not bucket_name:
        bucket_name = BOTO_S3_BUCKET
    return "https://{}.s3.amazonaws.com/{}/{}".format(bucket_name, folder_name, file_name)


def build_local_path(file_name, request=None):
    # TODO Fix this to exact path.
    url_prefix = settings.BASE_URL
    if request:
        url_prefix = '{scheme}://{host}'.format(scheme=request.scheme,
                                                host=request.get_host())
    return url_prefix + "/media/%s" % file_name

def gen_order_id_booking(row):
    import time, random
    try:
        row.order_id = str(int(time.mktime(row.created_at.timetuple()))) + str(random.randint(10,99)) + str(row.user_id)
        for row_hist in row.history.all():
            row_hist.order_id = row.order_id
        row.save()
    except:
        gen_order_id_booking(row)


def validate_uploaded_files(files):
    import os
    ext_whitelist = [i.lower() for i in settings.BILL_UPLOAD_ALLOWED_EXTENSIONS]
    for uploaded_file in files:
        filename = uploaded_file.name
        ext = os.path.splitext(filename)[1]
        ext = ext.lower()
        if ext not in ext_whitelist:
            raise Exception('Not a valid File Type')
    return True


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def custom_sql(query, params=None):
    """
    :param query: %s if required
    :param params: []
    :return:
    """
    with connection.cursor() as c:
        c.execute(query, params)
        return dictfetchall(c)


def namedtuplefetchall(cursor):
    from collections import namedtuple
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def get_cols_as_list_of_values(query, params=None):
    with connection.cursor() as c:
        c.execute(query, params)
        return c.fetchall()


def username_to_uuid(value):
    return uuid.uuid4()


def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    backend = kwargs.get('backend')
    if user and user.email:
        return # The user we're logging in already has their email attribute set
    elif is_new and not details.get('email'):
        # If we're creating a new user, and we can't find the email in the details
        # we'll attempt to request it from the data returned from our backend strategy
        userEmail = strategy.request_data().get('email')
        if userEmail:
            details['email'] = userEmail


def save_user_data(backend, user, response, *args, **kwargs):
    if backend.name == 'facebook':
        user.name = response.get('name')
        user.save()


def build_response(status, data=None, message=None):
    """
        following response standard: http://labs.omniti.com/labs/jsend
    """
    response_dict = {}
    if status == constants.RESPONSE_STATUS_SUCCESS:
        response_dict = {
            'status': constants.RESPONSE_STATUS_SUCCESS,
            'data': data,
            'message':message
        }
    elif status == constants.RESPONSE_STATUS_FAIL:
        response_dict = {
            'status': constants.RESPONSE_STATUS_FAIL,
            'data': data,
            'message':message
        }
        return HttpResponse(ujson.dumps(response_dict), status=400)
    elif status == constants.RESPONSE_STATUS_ERROR:
        response_dict = {
            'status': constants.RESPONSE_STATUS_ERROR,
            'data': data,
            'message': message
        }
        return HttpResponse(ujson.dumps(response_dict), status=500)

    return HttpResponse(ujson.dumps(response_dict))


def capture_razor_pay_payment(razor_payment_id, amount_in_paise, booking_id, bumper_payment_id):
    logger.debug('Razor_payment_id=%s, Booking_id=%s, bumper_payment_id=%s' %
                 (razor_payment_id,booking_id,bumper_payment_id))

    response_from_razor = None
    try:
        url = 'https://api.razorpay.com/v1/payments/%s/capture' % razor_payment_id
        resp = requests.post(url, data={'amount': amount_in_paise}, auth=(settings.RAZOR_PAY_API_KEY,
                                                                          settings.RAZOR_PAY_API_SECRET))
        if resp and resp.status_code == 200:
            # Payment captured.
            from core.models.payment import Payment
            payment = Payment.objects.filter(id=bumper_payment_id).first()
            if payment:
                payment.payment_vendor_id = razor_payment_id
                payment.tx_status = Payment.TX_STATUS_SUCCESS
                payment.vendor_status = resp.json().get('status')
                payment.save()

            return True
        else:
            response_from_razor = resp.json()
            logger.error('Failed to capture payment.booking_id=%s, Payment_id=%s, amount=%s, resp=%s' %
                         (booking_id, bumper_payment_id, amount_in_paise, response_from_razor))
            raise Exception('unable to capture response from Razor pay. %s' % response_from_razor)
    except:
        logger.exception('Failed to capture payment. Payment_id=%s, amount=%s' % (bumper_payment_id, amount_in_paise))

        from services.email_service import NewEmailService
        from core.models.message import Messages
        email_service = NewEmailService(
            to_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_TO_LIST,
            cc_list=settings.ALERT_EMAIL_PAYMENT_FAILURE_CC_LIST,
            bcc_list=[],
            context={},
            email_format='html',
            analytic_info={
                'booking_id': booking_id
            },
            message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS)

        email_service.send(
            email_body='Failed to capture payment.booking_id=%s, Payment_id=%s, amount=%s, response from Razor=%s' %
                       (booking_id, bumper_payment_id, amount_in_paise, response_from_razor),
            subject='Bumper: Razor Pay, unable to capture payment [BookingID:%s]' % booking_id,
            template_folder_name=None)


def get_challan_by_reg_num(reg_num):
    """

    :param reg_num: dict with text1, text2, text3, text4
    :return:
    """
    resp = requests.get('http://www.bangaloreone.gov.in/public/BPSPayByRegistrationNumber.aspx')
    logger.debug('STatus Code for get %s' % resp.status_code)
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        all_data = {}
        for link in soup.find_all('input'):
            all_data[link.get('name')] = link.get('value')

        all_data['txtRegNumber1'] = 'KA'
        all_data['txtRegNumber2'] = '01'
        all_data['txtRegNumber3'] = 'MM'
        all_data['txtRegNumber4'] = '1022'
        all_data['rdbCardType'] = 'M'

        logger.debug('Data from get %s' % all_data)

        resp2 = requests.post('http://www.bangaloreone.gov.in/public/BPSPayByRegistrationNumber.aspx', data=all_data)
        logger.debug('STatus Code after post %s' % resp2.status_code)
        soup1 = BeautifulSoup(resp2.text, 'html.parser')
        result_data = {}
        for link in soup1.find_all('input'):
            result_data[link.get('name')] = link.get('value')

        logger.debug('Data from post %s' % result_data)

        logger.debug('Raw HTML after post %s' % resp2.text)


def get_device_dict(user):
    from core.managers.userManager import get_user_active_devices
    user_devices = get_user_active_devices(user)
    device_type_count_list = user_devices.values('device_type').annotate(num_devices=Count('device_type'))
    device_type_dict = {}
    for device_type_count_dict in device_type_count_list:
        device_type_dict[device_type_count_dict.get('device_type')] = device_type_count_dict.get('num_devices')
    return device_type_dict


def update_booking_change_to_localytics(user, status_id, status_desc):
    if not settings.SEND_STATUS_CHANGE_TO_LOCALYTICS:
        return
    from constants import DEVICE_TYPE_ANDROID
    device_type_dict = get_device_dict(user)
    # Check if user has active android device
    if device_type_dict.get(DEVICE_TYPE_ANDROID):
        url = 'https://profile.localytics.com/v1/profiles/%d' % user.id
        headers = {'Content-Type': 'application/json'}
        auth = HTTPBasicAuth('7538defbb583b2640de0dc2-af993e68-23ed-11e6-44b0-00adad38bc8d',
                             '6bf73d0bd5b9d46e5dc606d-af9941b0-23ed-11e6-44b0-00adad38bc8d')
        data = {'attributes': {'status_id': '%d' % status_id, 'status_desc': '%s' % status_desc}}
        r = requests.post(url, ujson.dumps(data), headers=headers, auth=auth)
        if r.status_code == 202:
            logger.info('Booking change to Localytics user=%s, status=%s' % (user.id, status_id))
        else:
            logger.error('Booking change to Localytics failed for user=%s, status=%s with status_code=%s' %
                         (user.id,status_id,r.status_code))


def update_event_to_localytics(user, event_name, attrs):
    logger.info("LOCALYTICS_EVENT:: update_localytics_event_api_call with event_name: %s and user: %s and "
                "attributes: %s" % (event_name, user, attrs))
    if not settings.SEND_STATUS_CHANGE_TO_LOCALYTICS:
        return
    current_time_in_ms = int(round(time.time() * 1000))
    # since the Localytics Events API is in Beta, api_version is v0 in the following url
    url = 'https://analytics.localytics.com/events/v0/uploads'
    headers = {'Content-Type': 'application/json'}
    from constants import DEVICE_TYPE_ANDROID, DEVICE_TYPE_IOS
    device_type_dict = get_device_dict(user)
    # check if user has active android device
    if device_type_dict.get(DEVICE_TYPE_ANDROID):
        logger.info("LOCALYTICS_EVENT:: Device type is Android")
        auth = HTTPBasicAuth(settings.LOCALYTICS_ANDROID_API_KEY, settings.LOCALYTICS_ANDROID_APP_SECRET)
        app_uuid = settings.LOCALYTICS_ANDROID_APP_ID
    elif device_type_dict.get(DEVICE_TYPE_IOS):
        # auth = HTTPBasicAuth(settings.LOCALYTICS_IPHONE_API_KEY, settings.LOCALYTICS_IPHONE_APP_SECRET)
        # app_uuid = settings.LOCALYTICS_IPHONE_APP_ID
        logger.info("LOCALYTICS_EVENT:: iPhone api key and secret for localytics is not there")
        return False
    else:
        logger.info("LOCALYTICS_EVENT:: User does not have android or iphone device")
        return False

    parameters = {'schema_url': 'https://localytics-files.s3.amazonaws.com/schemas/eventsApi/v0.json',
                  'app_uuid': app_uuid,
                  'customer_id': str(user.id),
                  'event_name': event_name,
                  'event_time': current_time_in_ms,
                  'uuid': str(uuid.uuid4()),
                  "attributes": attrs}
    logger.info('LOCALYTICS_EVENT:: The parameters which is passed are as follows: %s' % parameters)

    r = requests.post(url, json=parameters, headers=headers, auth=auth)
    try:
        if r.status_code == 202:
            logger.info('LOCALYTICS_EVENT:: %s Event has been successfully added to Localytics for '
                        'customer_id: %s' % (event_name, user.id))
        else:
            logger.info('LOCALYTICS_EVENT:: %s Event is not added to Localytics for customer_id: %s with status_code: %s '
                        'and json output is:%s' % (event_name,user.id,r.status_code,r.content))
    except Exception:
        logger.info('LOCALYTICS_EVENT:: Failing in this update_event_to_localytics')


def capitalize_words(s):
    return re.sub(r'\w+', lambda m:m.group(0).capitalize(), s)


def pdf(template, context):
    html_string = render_to_string(template,context=context)
    html = HTML(string=html_string)
    html.write_pdf(target='/tmp/mypdf.pdf')
    f = open('/tmp/mypdf.pdf', 'r')
    return f


def handle_car_pickup_incentive(booking):
    from core.models.booking import UserVendorCash, Booking
    from core.models.users import ScratchFinderLead
    sflead = ScratchFinderLead.objects.filter(phone=booking.user.phone
                                              ).exclude(status=ScratchFinderLead.STATUS_REJECTED).first()
    if not sflead:
        return
    if Booking.objects.filter(status__flow_order_num__range=(9,24),
                              user=booking.user).exclude(id=booking.id).exists():
        logger.info("No SF Incentive - Existing converted bookings for this booking ({}) user ({})".format(booking.id,
                                                                                                        booking.user_id))
        return
    # create incentives if any
    incentive_data = {"name": "INCENTIVE_EVENT_SFLEAD_CREATE",
                      "entity": UserVendorCash.ENTITY_SFLEAD,
                      "entity_id": sflead.id,
                      "user": sflead.user,
                      "transferred": True,
                      "transfer_info": "For Booking: {}".format(booking.id)
                      }
    from core.managers import userManager
    uvc = userManager.handle_incentive_events(incentive_data)
    if uvc:
        from core.tasks import send_custom_notification_task
        send_custom_notification_task.delay('USER_SMS_SCRATCH_LEAD_CONVERTED',
                                            {'amount': uvc.amount},
                                            user_id=sflead.user_id)


def handle_car_pickup_referral(booking):
    from core.models.referral import Referral
    from core.managers import userManager
    referral = Referral.objects.filter(referred=booking.user).first()
    if referral:
        logger.info("Handling Car pickup Referral for booking: %s", booking.id)
        flow_name = "CAR_PICKED_UP"
        userManager.handle_referral_campaign(flow_name, referral)
