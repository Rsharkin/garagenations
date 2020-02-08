from django.shortcuts import render_to_response, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from core.managers.paymentManager import process_payment_response
from core.managers.generalManager import process_sms_delivery_callback
from core.models.payment import Payment
from core.models.users import UserEmailVerify
from core.models.booking import Booking, BookingInvoice, BookingProformaInvoice
from django.conf import settings
from core.utils import build_response
from core import constants
from core.forms import PhoneNumberForm
from core.tasks import capture_razor_pay_payment
from django.http import HttpResponse
import ujson
import decimal
import logging
logger = logging.getLogger(__name__)
mobile_uas = [
    'w3c ', 'acs-', 'alav', 'alca', 'amoi', 'audi', 'avan', 'benq', 'bird', 'blac',
    'blaz', 'brew', 'cell', 'cldc', 'cmd-', 'dang', 'doco', 'eric', 'hipt', 'inno',
    'ipaq', 'java', 'jigs', 'kddi', 'keji', 'leno', 'lg-c', 'lg-d', 'lg-g', 'lge-',
    'maui', 'maxo', 'midp', 'mits', 'mmef', 'mobi', 'mot-', 'moto', 'mwbp', 'nec-',
    'newt', 'noki', 'oper', 'palm', 'pana', 'pant', 'phil', 'play', 'port', 'prox',
    'qwap', 'sage', 'sams', 'sany', 'sch-', 'sec-', 'send', 'seri', 'sgh-', 'shar',
    'sie-', 'siem', 'smal', 'smar', 'sony', 'sph-', 'symb', 't-mo', 'teli', 'tim-',
    'tosh', 'tsm-', 'upg1', 'upsi', 'vk-v', 'voda', 'wap-', 'wapa', 'wapi', 'wapp',
    'wapr', 'webc', 'winw', 'winw', 'xda', 'xda-'
]

mobile_ua_hints = ['SymbianOS', 'Opera Mini', 'iPhone','Mobile Safari']


def mobileBrowser(request):
    ''' Super simple device detection, returns True for mobile devices '''

    mobile_browser = False
    ua = request.META.get('HTTP_USER_AGENT','unknown').lower()[0:4]

    if (ua in mobile_uas):
        mobile_browser = True
    else:
        for hint in mobile_ua_hints:
            if request.META.get('HTTP_USER_AGENT','unknown').find(hint) > 0:
                mobile_browser = True

    return mobile_browser


def login_required_ajax(function=None, redirect_field_name=None):
    """
    Just make sure the user is authenticated to access a certain ajax view

    Otherwise return a HttpResponse 401 - authentication required
    instead of the 302 redirect of the original Django decorator
    """
    def _decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse(status=401)
        return _wrapped_view

    if function is None:
        return _decorator
    else:
        return _decorator(function)


def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response

def index(request, template_name, param=None):
    if mobileBrowser(request):
        template_name = 'public/m_index.html'
    context = {
        'opbeatOrgId': settings.OPBEAT_WEBSITE.get('ORGANIZATION_ID'),
        'opbeatAppId': settings.OPBEAT_WEBSITE.get('APP_ID'),
        'LOCALYTICS_KEY': settings.__getattr__('LOCALYTICS_KEY'),
        'GOOGLE_ANALYTICS_UNIVERSAL_KEY': settings.__getattr__('GOOGLE_ANALYTICS_UNIVERSAL_KEY'),
        'show_chat_option': getattr(settings, 'SHOW_CHAT_OPTION', False),
        'chat_option_to_show': getattr(settings, 'CHAT_OPTION_TO_SHOW', ''),
    }
    return render_to_response(template_name, context=context, context_instance=RequestContext(request))


@login_required(login_url='auth_login')
def ops_index(request, template_name, param=None):
    """
        This is different from index because this is always open authenticated.
    :param request:
    :param template_name:
    :param param:
    :return:
    """
    return render_to_response(template_name, context={}, context_instance=RequestContext(request))


@login_required(login_url='auth_login')
def index_with_two_params(request, template_name,param=None, param2=None):
    return render_to_response(template_name, context={}, context_instance=RequestContext(request))


@login_required(login_url='auth_login')
def index_with_three_params(request, template_name,param=None, param2=None, param3=None):
    return render_to_response(template_name, context={}, context_instance=RequestContext(request))


@login_required(login_url='auth_login')
def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect(reverse('auth_login'))


def forgot_password(request, template_name):
    from core.forms import ForgotPasswordForm
    from core.models.users import BumperUser

    forgot_pass_form = ForgotPasswordForm()
    if request.method == 'POST':
        forgot_pass_form = ForgotPasswordForm(request.POST)
        if forgot_pass_form.is_valid():
            phone = forgot_pass_form.cleaned_data
            bu = BumperUser.objects.get(ops_phone=phone)
            bu.reset_password()
            return HttpResponseRedirect(reverse('auth_login'))

    return render_to_response(template_name, context={"form": forgot_pass_form}, context_instance=RequestContext(request))


@login_required(login_url='auth_login')
def change_password(request):
    from core.forms import ChangePasswordForm
    if request.method == 'POST':
        change_pass_form = ChangePasswordForm(request.POST)
        if change_pass_form.is_valid():
            password = change_pass_form.cleaned_data.get('password')
            request.user.set_password(password)
            request.user.save()
            return build_response(constants.RESPONSE_STATUS_SUCCESS, message='Password Changed', data={})
        else:
            errors=[]
            errors.append(change_pass_form.errors.as_ul())
            errors.append(change_pass_form.non_field_errors().as_ul())
            return build_response(constants.RESPONSE_STATUS_FAIL, data=errors, message=constants.FORM_ERROR_MESSAGE)

    return render_to_response('ops-panel/index.html', context={}, context_instance=RequestContext(request))


@csrf_exempt
def sms_delivery_webhook(request):
    logger.debug('Request Data from SMS Delivery Webhook %s' % request.REQUEST)
    process_sms_delivery_callback(request.REQUEST)
    return HttpResponse(status=200)


@csrf_exempt
def payment_payu_success(request, template_name):
    logger.debug('Request Data from payu success url %s' % request.POST)
    payment_data = {}
    payment_data['vendor_id'] = request.POST.get('payuMoneyId')
    payment_data['booking_id'] = request.POST.get('txnid')
    payment_data['net_amount_debit'] = request.POST.get('net_amount_debit',request.POST.get('amount'))
    payment_data['status'] = request.POST.get('status')
    payment_data['error_message'] = request.POST.get('error_Message')
    payment_data['vendor'] = Payment.VENDOR_PAYU_MONEY
    process_payment_response(payment_data, request.POST)
    return render_to_response(template_name, context={'data': request.POST}, context_instance=RequestContext(request))


@csrf_exempt
def payment_payu_failure(request, template_name):
    logger.debug('Request Data from payu failure url %s' % request.POST)
    payment_data = {}
    payment_data['vendor_id'] = request.POST.get('payuMoneyId')
    payment_data['booking_id'] = request.POST.get('txnid')
    payment_data['net_amount_debit'] = request.POST.get('net_amount_debit',request.POST.get('amount'))
    payment_data['status'] = request.POST.get('status')
    payment_data['error_message'] = request.POST.get('error_Message')
    payment_data['vendor'] = Payment.VENDOR_PAYU_MONEY
    process_payment_response(payment_data, request.POST)
    return render_to_response(template_name, context={'data': request.POST}, context_instance=RequestContext(request))


@csrf_exempt
def payment_payu_webhook(request, template_name):
    logger.debug('Request Data from payu webhook %s' % request.body)
    json_data = ujson.loads(request.body)
    payment_data = {}
    payment_data['vendor_id'] = json_data.get('paymentId')
    payment_data['booking_id'] = json_data.get('merchantTransactionId')
    payment_data['net_amount_debit'] = json_data.get('amount')
    payment_data['vendor_status'] = json_data.get('status')
    payment_data['error_message'] = json_data.get('error_Message')
    payment_data['vendor'] = Payment.VENDOR_PAYU_MONEY
    if str(json_data.get('status')).upper() in ['SUCCESS', 'RELEASE PAYMENT', 'SETTLEMENT IN PROCESS']:
        payment_data['status'] = 'success'
    process_payment_response(payment_data, json_data)
    return render_to_response(template_name, context={'data': json_data}, context_instance=RequestContext(request))


@csrf_exempt
def payment_citrus_pay(request, template_name, redirect_to_website=0):
    logger.debug('Request Data from Citrus success url %s' % request.POST)
    try:
        booking_id_param = request.POST.get('bookingId')
        booking_id = booking_id_param[0] if isinstance(booking_id_param, (list, tuple)) else booking_id_param

        payment_id_param = request.POST.get('paymentId')
        payment_id = payment_id_param[0] if isinstance(payment_id_param, (list, tuple)) else payment_id_param

        device_type_param = request.POST.get('deviceType')
        device_type = device_type_param[0] if isinstance(device_type_param, (list, tuple)) else device_type_param

        invoice_id_param = request.POST.get('invoiceId')
        invoice_id = invoice_id_param[0] if isinstance(invoice_id_param, (list, tuple)) else invoice_id_param

        proforma_invoice_id_param = request.POST.get('proformaInvoiceId')
        proforma_invoice_id = proforma_invoice_id_param[0] if isinstance(proforma_invoice_id_param, (list, tuple)) else proforma_invoice_id_param

        if not booking_id:
            booking_id = request.POST.get('TxId')

        secret_key = settings.CITRUS_MERCHANT_SECRET_KEY
        verify_str = ''
        if request.POST.get('TxId'):
            verify_str += request.POST.get('TxId')
        if request.POST.get('TxStatus'):
            verify_str += request.POST.get('TxStatus')
        if request.POST.get('amount'):
            verify_str += request.POST.get('amount')
        if request.POST.get('pgTxnNo'):
            verify_str += request.POST.get('pgTxnNo')
        if request.POST.get('issuerRefNo'):
            verify_str += request.POST.get('issuerRefNo')
        if request.POST.get('authIdCode'):
            verify_str += request.POST.get('authIdCode')
        if request.POST.get('firstName'):
            verify_str += request.POST.get('firstName')
        if request.POST.get('lastName'):
            verify_str += request.POST.get('lastName')
        if request.POST.get('pgRespCode'):
            verify_str += request.POST.get('pgRespCode')
        if request.POST.get('addressZip'):
            verify_str += request.POST.get('addressZip')

        response_signature = request.POST.get('signature')
        import hmac, hashlib
        signature = hmac.new(secret_key, verify_str, hashlib.sha1).hexdigest()

        if not response_signature and str(response_signature) != '' and str(response_signature).upper() \
                != str(signature).upper():
            logger.error('Citrus Response Signature and Our (Merchant) Signature Mis-Mactch')
            return render_to_response("payment/citrus-fail.html",
                                      context={'json_dump': '{"Error" : "Transaction Failed","Reason" : '
                                                            '"Signature Verification Failed"}'},
                                      context_instance=RequestContext(request))

        cleaned_data = {}
        for key, value in request.POST.iteritems():
            cleaned_data[key] = value[0] if isinstance(value, (list, tuple)) else value
        """
        Dummy response from citrus pay.
        <QueryDict: {u'addressState': [u'Maharashtra'], u'cardHolderName': [u'PRAVIN RAJ'], u'expiryMonth':
        [u''], u'currency': [u''], u'dccCurrency': [u''], u'TxGateway': [u'HDFC PG (Citrus Plus)'], u'expiryYear': [u''], u'pgTxnNo': [u'3796705281260121'], u'mobileNo': [u'9535649530'], u'
        encryptedCardNumber': [u''], u'addressCountry': [u'India'], u'TxMsg': [u'Transaction Successful'], u'authIdCode': [u'999999'], u'txn3DSecure': [u''], u'impsMobileNumber': [u''], u'e
        mail': [u'pravin.raj@autoninja.in'], u'txnType': [u'SALE'], u'isCOD': [u'false'], u'exchangeRate': [u''], u'addressStreet1': [u'streetone'], u'eci': [u''], u'cardType': [u'MCRD'], u
        'maskedCardNumber': [u'549176XXXXXX3000'], u'cardCode': [u''], u'txnDateTime': [u'2016-01-12 12:28:41'], u'transactionId': [u'554019'], u'addressCity': [u'Mumbai'], u'dccOfferId': [
        u''], u'requestedAmount': [u''], u'firstName': [u'Tester'], u'lastName': [u'Citrus'], u'TxStatus': [u'SUCCESS'], u'dccAmount': [u''], u'paymentMode': [u'CREDIT_CARD'], u'TxId': [u'1
        45258171360969'], u'requestedCurrency': [u''], u'amount': [u'6.00'], u'addressStreet2': [u''], u'impsMmid': [u''], u'TxRefNo': [u'CTX1601120658412286905'], u'signature': [u'f3f6b450
        3286740a640c53ce8a108efb580dd54a'], u'issuerRefNo': [u'601228424531'], u'pgRespCode': [u'0'], u'addressZip': [u'400052']}>
        """
        json_data = {}
        json_data['vendor'] = Payment.VENDOR_CITRUS_PAY
        json_data['vendor_id'] = cleaned_data.get('TxRefNo')
        json_data['booking_id'] = booking_id  # check a mapping.
        json_data['payment_id'] = payment_id
        json_data['device_type'] = device_type
        json_data['invoice_id'] = invoice_id
        json_data['proforma_invoice_id'] = proforma_invoice_id
        json_data['net_amount_debit'] = cleaned_data.get('amount')
        json_data['error_message'] = cleaned_data.get('TxMsg')
        json_data['vendor_status'] = cleaned_data.get('TxStatus')  # SUCCESS, FAIL, CANCEL
        if str(cleaned_data.get('TxStatus')).upper() in ['SUCCESS']:
            json_data['status'] = 'success'
        process_payment_response(json_data, cleaned_data)

        json_string = ujson.dumps(cleaned_data)
        logger.debug('Citrus json_string = %s' % json_string)
        if json_data.get('status') == 'success':
            return render_to_response(template_name, context={'json_dump': json_string,
                                                              'redirect_to_website': redirect_to_website,
                                                              'booking_id': booking_id,
                                                              'amount': json_data.get('net_amount_debit'),
                                                              },
                                      context_instance=RequestContext(request))
        else:
            return render_to_response("payment/citrus-fail.html", context={'json_dump': json_string,
                                                                           'redirect_to_website': redirect_to_website,
                                                                           'booking_id': booking_id,
                                                                           'amount': json_data.get('net_amount_debit'),
                                                                           },
                                      context_instance=RequestContext(request))
    except:
        logger.exception('Failed to process Citrus Payment')
        raise


@csrf_exempt
def payment_razor_pay(request, template_name):
    logger.debug('Request Data from Razor success url %s' % request.body)

    try:
        json_data = ujson.loads(request.body)
        if json_data.get('payload') and json_data['payload'].get('payment') and json_data['payload']['payment'].get(
                'entity'):

            payment_entity = json_data['payload']['payment'].get('entity')
            notes_entity = json_data['payload']['payment']['entity'].get('notes')

            if notes_entity:
                booking_id = notes_entity.get('bookingId')
                payment_id = notes_entity.get('paymentId')
                device_type = notes_entity.get('deviceType')
                invoice_id = notes_entity.get('invoiceId')
                proforma_invoice_id = notes_entity.get('proformaInvoiceId')
                used_credits = notes_entity.get('used_credits')

                payment_data = {}
                payment_data['vendor'] = Payment.VENDOR_RAZOR_PAY
                payment_data['vendor_id'] = payment_entity.get('id')
                payment_data['booking_id'] = booking_id  # check a mapping.
                payment_data['payment_id'] = payment_id
                payment_data['device_type'] = device_type
                payment_data['invoice_id'] = invoice_id
                payment_data['proforma_invoice_id'] = proforma_invoice_id
                payment_data['used_credits'] = used_credits
                #  amount is coming in paisa  and not rupees.
                # If int is not coming then let it be empty and ops raise alert.
                net_amount_debit = decimal.Decimal(payment_entity.get('amount'))/decimal.Decimal('100.00')
                payment_data['net_amount_debit'] = net_amount_debit

                payment_data['error_message'] = payment_entity.get('error_description')
                payment_data['vendor_status'] = payment_entity.get('status')

                if str(payment_entity.get('status')).upper() in ['SUCCESS', 'AUTHORIZED']:
                    payment_data['status'] = 'success'
                else:
                    payment_data['status'] = 'failed'

                try:
                    payment_id = process_payment_response(payment_data, json_data)
                except Exception as e:
                    raise e
                finally:
                    if payment_data['status'] == 'success':
                        capture_razor_pay_payment.delay(payment_entity.get('id'), payment_entity.get('amount'),
                                                        booking_id, payment_id)

                return render_to_response(template_name, context={}, context_instance=RequestContext(request))
            else:
                logger.debug('Razor pay missing notes_entity =%s' % payment_entity)
        else:
            logger.debug('Razor pay missing payload or payment or entity dict json=%s' % json_data)
    except:
        logger.exception('Failed to process Razor payment')

    return render_to_response("payment/citrus-fail.html", context={}, context_instance=RequestContext(request))

@csrf_exempt
def citrus_bill_generator(request):
    logger.debug('Citrus Pay Bill gen url %s' % request.REQUEST)
    access_key = settings.CITRUS_MERCHANT_ACCESS_KEY
    secret_key = settings.CITRUS_MERCHANT_SECRET_KEY
    return_url = settings.CITRUS_RETURN_URL
    txnid_append_text = settings.TXNID_APPEND_TEXT

    value = request.REQUEST.get('amount', 0)
    booking_id = request.REQUEST.get('bookingId')
    payment_id = request.REQUEST.get('paymentId')
    discount_info = request.REQUEST.get('discountInfo')
    device_type = request.REQUEST.get('deviceType')
    invoice_id = request.REQUEST.get('invoiceId')
    proforma_invoice_id = request.REQUEST.get('proformaInvoiceId')

    invoice = None
    proforma_invoice = None
    payment = None

    if invoice_id:
        invoice = BookingInvoice.objects.filter(id=invoice_id,
                                                status=BookingInvoice.INVOICE_STATUS_PENDING).first()
    if proforma_invoice_id:
        proforma_invoice = BookingProformaInvoice.objects.filter(id=proforma_invoice_id,
                                                                 status=BookingProformaInvoice.INVOICE_STATUS_PENDING).first()

    if not invoice and not proforma_invoice:
        invoice = BookingInvoice.objects.filter(booking_id=booking_id,
                                                status=BookingInvoice.INVOICE_STATUS_PENDING).first()

    if proforma_invoice:
        payment = Payment.objects.filter(proforma_invoice=proforma_invoice,
                                         tx_status=Payment.TX_STATUS_PENDING).first()
    if invoice:
        payment = Payment.objects.filter(invoice=invoice,
                                         tx_status=Payment.TX_STATUS_PENDING).first()

    if not payment:
        return HttpResponse(ujson.dumps('{"status":"Invalid Data"}'))

    import time, random, hmac, hashlib

    txnid = str(booking_id)+ txnid_append_text + str(int(time.time())) + str(int(random.random() * 99999) + 10000)
    data_string = 'merchantAccessKey=%s&transactionId=%s&amount=%s' % (access_key, txnid, value)
    signature = hmac.new(secret_key, data_string, hashlib.sha1).hexdigest()

    amount = {"value": value, "currency": 'INR'}

    bill = {
        "merchantTxnId": txnid,
        "amount": amount,
        "requestSignature": signature,
        "merchantAccessKey": access_key,
        "returnUrl": return_url,
        "notifyUrl": return_url,
        "customParameters":{"bookingId": booking_id, "discountInfo": discount_info, "paymentId":payment_id,
                            "deviceType": device_type, "invoiceId": invoice_id,
                            "proformaInvoiceId": proforma_invoice_id},
    }

    payment.merchant_trx_id = txnid
    payment.device_type = device_type
    payment.save()

    logger.debug('Citrus Pay Bill details sent %s' % bill)
    return HttpResponse(ujson.dumps(bill))


def _citrus_bill_generation_processor(request):
    secret_key = settings.CITRUS_MERCHANT_SECRET_KEY
    vanity_url = settings.CITRUS_VANITY_URL
    txnid_append_text = settings.TXNID_APPEND_TEXT
    currency = "INR"

    value = request.REQUEST.get('amount', 0)
    booking_id = request.REQUEST.get('bookingId')
    payment_id = request.REQUEST.get('paymentId')
    device_type = request.REQUEST.get('deviceType')
    discount_info = request.REQUEST.get('discountInfo')
    invoice_id = request.REQUEST.get('invoiceId')
    proforma_invoice_id = request.REQUEST.get('proformaInvoiceId')

    invoice = None
    proforma_invoice = None
    payment = None

    if invoice_id:
        invoice = BookingInvoice.objects.filter(id=invoice_id,
                                                status=BookingInvoice.INVOICE_STATUS_PENDING).first()
    if proforma_invoice_id:
        proforma_invoice = BookingProformaInvoice.objects.filter(id=proforma_invoice_id,
                                                                 status=BookingProformaInvoice.INVOICE_STATUS_PENDING).first()

    if not invoice and not proforma_invoice:
        invoice = BookingInvoice.objects.filter(booking_id=booking_id,
                                                status=BookingInvoice.INVOICE_STATUS_PENDING).first()

    if proforma_invoice:
        payment = Payment.objects.filter(proforma_invoice=proforma_invoice,
                                         tx_status=Payment.TX_STATUS_PENDING).first()
    if invoice:
        payment = Payment.objects.filter(invoice=invoice,
                                         tx_status=Payment.TX_STATUS_PENDING).first()

    if not payment:
        return HttpResponse(ujson.dumps('{"status":"Invalid Data"}'))

    import time, random, hmac, hashlib

    txnid = str(booking_id)+ txnid_append_text + str(int(time.time())) + str(int(random.random() * 99999) + 10000)
    data_string = '%s%s%s%s' % (vanity_url, value, txnid, currency)
    signature = hmac.new(secret_key, data_string, hashlib.sha1).hexdigest()

    booking = Booking.objects.get(id=booking_id)

    payment.merchant_trx_id = txnid
    payment.device_type = device_type
    payment.save()

    return {
        "formPostUrl": settings.CITRUS_FORM_POST_URL,
        "merchantTxnId": txnid,
        "orderAmount": value,
        "currency": currency,
        "secSignature": signature,
        "notifyUrl": settings.CITRUS_RETURN_URL,
        "name": booking.user.name,
        "phoneNumber": booking.user.phone,
        "email": booking.user.email,
        "customParameters": {
            "bookingId": booking_id,
            "discountInfo": discount_info,
            "paymentId": payment_id,
            "deviceType": device_type,
            "invoiceId": invoice_id,
            "proformaInvoiceId": proforma_invoice
        },
    }


@csrf_exempt
def citrus_bill_generator_web(request):
    logger.debug('WEB Citrus Pay Bill gen url for %s' % request.REQUEST)
    bill = _citrus_bill_generation_processor(request)
    bill['returnUrl'] = settings.CITRUS_WEBSITE_RETURN_URL
    logger.debug('WEB Citrus Pay Bill details sent %s' % bill)
    return HttpResponse(ujson.dumps(bill))


@csrf_exempt
def citrus_bill_generator_ios(request):
    logger.debug('IOS Citrus Pay Bill gen url for IOS %s' % request.REQUEST)
    bill = _citrus_bill_generation_processor(request)
    bill['returnUrl'] = settings.CITRUS_RETURN_URL
    logger.debug('IOS Citrus Pay Bill details sent %s' % bill)
    return HttpResponse(ujson.dumps(bill))


def verify_email(request):
    from django.shortcuts import redirect
    try:
        verification_key = request.REQUEST.get('actkey')
        email = request.REQUEST.get('email')
        if not verification_key or not email:
            raise Http404()

        User = get_user_model()
        users = User.objects.filter(email=email)
        if users:
            verifykeyobj = UserEmailVerify.objects.filter(user__in=users, key=verification_key)
            if verifykeyobj:
                users.update(is_email_verified=True)
                verifykeyobj.delete()
        return redirect("https://bumper.com/?utm_source=email_verification&utm_medium=email&utm_campaign=email_verification")
    except Http404:
        logger.exception("Exception in verify email. - verification key not present or email not present.")
        raise Http404
    except:
        logger.exception("Exception in verify email.")
        return redirect("https://bumper.com/?utm_source=email_verification&utm_medium=email&utm_campaign=email_verification")


@csrf_exempt
def send_sms_with_app_link(request):
    logger.debug('Request for app link %s' % request.REQUEST)
    if request.method == 'POST':
        try:
            phone_form = PhoneNumberForm(request.POST)
            if phone_form.is_valid():
                from core.models.users import BumperUser
                from services.sms_service import SMSService
                from core.constants import SMS_TEMPLATES, SMS_TEMPLATE_NEW_LEAD
                phone = phone_form.cleaned_data
                sms_service = SMSService(BumperUser.objects.get(id=1))
                sms_service.send_sms(phone, SMS_TEMPLATES[SMS_TEMPLATE_NEW_LEAD] % {'app_download_link':settings.BUMPER_APP_URL_FOR_APP_INSTALL})
                return HttpResponse(ujson.dumps({'status': 'sent'}))
            else:
                return HttpResponse(ujson.dumps({'status': 'Invalid Phone'}))
        except:
            logger.exception('Failed to send sms with app link')
            raise





# from rest_framework.decorators import api_view, renderer_classes
# from rest_framework import response, schemas
# from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
#
#
# @api_view()
# @renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
# def docs(request):
#     generator = schemas.SchemaGenerator(title='Bumper2 APIs')
#     return response.Response(generator.get_schema(request=request))