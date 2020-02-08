import requests
import ujson
from django.conf import settings
import logging
log = logging.getLogger(__name__)


class HTTPReqException(Exception): pass
class SMSFailedException(HTTPReqException): pass


class SMSService(object):
    """
        Class to hold the business logic for sending email 
    """
    from core.models.message import Messages

    sms_gateway_username = "bumper"
    sms_gateway_password = "bumper@@321"
    sms_gateway_url = "http://msg2all.com/IKONTELTRANSSMS/sendsms.jsp?"
    """
        $ph = implode(',', $ph); // work?
        $url = $api . "login=$un&passwd=$ps&msisdn=91$ph&msg=" . fullUrlEncode($msg);
    """
    url_si = 'http://api-alerts.solutionsinfini.com/v4/?'
    si_api_key = 'Abc82c0f5c94cc0a004f316e7c66e9730'

    user_sending_sms = None

    def __init__(self, user, sms_sender_code='BUMPER', message_send_level=Messages.MESSAGE_SEND_LEVEL_SPECIFIC,
                 direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_CUSTOMER, is_promo=False):
        self.user_sending_sms = user
        self.sender_code = sms_sender_code
        self.message_send_level = message_send_level
        self.direction = direction
        if is_promo:
            self.url_si = 'http://api-promo.solutionsinfini.com/v4/?'
            self.si_api_key = 'A5b2ac5995b60780040f549c1af6f0b3e'
            self.sender_code = 'BULKSMS'

    def construct_payload(self, data=None, is_json=True):
        """
        """
        payload = {}
        if is_json:
           return ujson.dumps(data)
        else:
            plaintext_data = data.copy()
            for k in plaintext_data.keys():
                plaintext_data['%s' % k] = plaintext_data.pop(k)
            payload.update(plaintext_data)

        if is_json:
            payload = ujson.dumps(payload)

        return payload

    def make_request(self, data):
        try:
            response = requests.get(self.sms_gateway_url, params=data)
        except requests.ConnectionError:
            log.exception('Failed to send SMS')
            raise SMSFailedException("There was an internal error in the SMS server while trying to process the request")
        return response

    def send_sms_ikontel(self, recipient, sms_text, *args, **kwargs):
        log.debug('Request to send sms(IKONTEL) from account=%s, sender_code=%s, to=%s, template=%s' %
                  (self.user_sending_sms, self.sender_code, recipient, sms_text))

        result = None
        data = {
                'version': 'v1.0',
                'login': self.sms_gateway_username,
                'passwd': self.sms_gateway_password,
                'msisdn': "91" + str(recipient),
                'msg': sms_text,
                'sender': self.sender_code,
            }

        payload = self.construct_payload(data, is_json=True)
        log.debug('Request data for SMS Gateway= %s' % payload)
        response = self.make_request(data)
        log.info('URL of SMS Gateway =%s' % response.url)
        try:
            response = str(response.text).strip()
            resp_json = ujson.decode(response)
            if str(resp_json['result']['status']['statusCode']) == "0":
                result = 'SENT'
            else:
                #failed status
                log.error('Sending SMS failed: response=%s' % response)
                result = str(resp_json['result']['status'])
                self.send_alert_email_for_failed_sms(recipient, self.sender_code, sms_text,'Autoninja', result)
        except:
            log.exception('Failed to parse sms gateway output')

        log.info('Response of SMS Gateway =%s' % response)

        return result, sms_text

    def make_request_si(self, recipient, sms_text, user_message_id=None):
        data = {
                'method': 'sms',
                'api_key': self.si_api_key,
                'to': recipient,
                'sender': self.sender_code,
                'message': sms_text,
                'unicode': 0,
                'dlrurl': settings.BASE_URL+'sms/delivery-status/',
                'custom': user_message_id,
            }
        log.debug('Request data for SMS Gateway_solutions_infinity= %s' % data)
        try:
            response = requests.get(self.url_si,params=data)
            log.debug('Response for SMS Gateway_solutions_infinity= %s' % response.text)
        except requests.ConnectionError:
            log.exception('Failed to send SMS')
            raise SMSFailedException("There was an internal error in the SMS server while trying to process the request")

        result = ujson.loads(response.text)
        try:
            if result.get('status') == 'OK':
                result = 'SENT'
            else:
                result = "%s - %s" % (result.get('status'), result.get('message'))
                self.send_alert_email_for_failed_sms(recipient, self.sender_code, sms_text,'Autoninja', result)
        except:
            log.exception('Failed to parse sms gateway output')

        return result, sms_text

    def send_sms(self, recipient, sms_text, analytic_info={}, *args, **kwargs):
        from core.models.message import Messages, MessageUser
        new_message = Messages.objects.create(
            message_type=Messages.MESSAGE_TYPE_SMS,
            message=sms_text,
            message_send_level=self.message_send_level,
            direction=self.direction,
            booking_id=analytic_info.get('booking_id'),
            action=analytic_info.get('action'),
            notification_id=analytic_info.get('notification_id'),
            sent_by_id=analytic_info.get('sent_by_id'),
            label=analytic_info.get('label'),
        )
        message_user = MessageUser.objects.create(
            user=self.user_sending_sms,
            message=new_message,
            sent_to=recipient,
            delivery_report='pending',
        )
        if str(recipient) not in settings.SMS_DND_LIST:
            if settings.SMS_DEFAULT_VENDOR == 'INFINIA':
                result, sms_text = self.make_request_si(recipient, sms_text,user_message_id=message_user.id)
            else:
                result, sms_text = self.send_sms_ikontel(recipient, sms_text)
        else:
            result = 'In our DND List'

        message_user.gateway_api_response = result
        message_user.save()

        return result, sms_text

    def send_alert_email_for_failed_sms(self,recipient,sender_code,sms_text,portal,errors):
        from services.email_service import NewEmailService
        email_service = NewEmailService(to_list=settings.SMS_FAILURE_ALERT_LIST)
        email_service.send(email_body='Failed to send SMS.\n (%s-%s)Phone=%s, sms=%s--Error=%s' %
                                           (portal, sender_code, recipient, sms_text, errors),
                           subject='Failed SMS alert!'
                           )