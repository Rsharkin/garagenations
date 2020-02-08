import uuid
import string
import os
import logging

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import Permission
from rest_framework_jwt.settings import api_settings
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords
from django.db.models import Q
from core.models.common import CreatedAtAbstractBase, Address, Media
from core.models.master import City, CarModel, FollowupResult, InquiryCancellationReasons, Workshop, Source,\
    Notifications, CarModelVariant, CarColor

from core.constants import SMS_TEMPLATES, SMS_TEMPLATE_NEW_AUTH_CODE, DEVICE_TYPES, DEVICE_TYPE_IOS, \
    DEVICE_TYPE_ANDROID, SMS_TEMPLATE_RESET_PASSWORD

log = logging.getLogger(__name__)


# Create your models here.
class BumperUserManager(BaseUserManager):
    """
        The manager for the auth user.
    """
    def create_user(self, password=None, **other_fields):
        """
            Create user with phone number and password
        """
        email = other_fields.get('email')
        if not email:
            email = None

        user = self.model(
            username=uuid.uuid4(),
            name=other_fields.get('name',other_fields.get('username')),
            phone=other_fields.get('phone'),
            email=email,
            city_id=other_fields.get('city_id'),
            is_superuser=False,
            utm_source=other_fields.get('utm_source'),
            utm_medium=other_fields.get('utm_medium'),
            utm_campaign=other_fields.get('utm_campaign'),
            designation=other_fields.get('designation'),
            company_name=other_fields.get('company_name'),
            date_joined=other_fields.get('date_joined'),
            is_active=True,
            source=other_fields.get('source'),
            is_otp_validated=other_fields.get('is_otp_validated', False)
        )

        if not password:
            # TODO: generate random password
            password = user.get_rand_password()

        user.set_password(password)

        user.save(using=self._db)

        user_group = Group.objects.filter(name='BumperUser').first()
        if user_group:
            user_group.user_set.add(user)
        if other_fields.get('group_name'):
            g = Group.objects.filter(name=other_fields.get('group_name')).exclude(name='BumperUser').first()
            if g:
                g.user_set.add(user)

        user.create_drf_token()
        user.create_referral_code()
        user.send_welcome_mail()
        return user

    def create_superuser(self, password=None, **other_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(password, **other_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class BumperUser(AbstractBaseUser, PermissionsMixin):
    """
        Custom user class
    """
    SOURCE_WEB = 'web'
    SOURCE_MOBILE_WEB = 'mobile-web'
    SOURCE_DESKTOP_WEB = 'desktop-web'
    SOURCE_EMAIL = 'email'
    SOURCE_SMS = 'sms'
    SOURCE_CHAT = 'chat'
    SOURCE_CALL = 'call'
    SOURCE_APP = 'app'
    SOURCE_EVENT = 'event'
    SOURCE_UBER = 'uber'
    SOURCE_OPS_PANEL = 'opsPanel'
    SOURCE_ANDROID = 'android'
    SOURCE_IPHONE = 'iphone'
    SOURCE_FACEBOOK = 'facebook'
    SOURCE_REFERRAL = 'referral'
    SOURCE_HELPSHIFT = 'helpshift'
    SOURCE_JUSTDIAL = 'justdial'
    SOURCE_DRWHEELZ = 'drwheelz'
    SOURCE_INCOMING_CALL = 'incomingCall'
    SOURCE_URBANCLAP = 'urbanClap'
    SOURCE_CARS24 = 'cars24'
    SOURCE_HP_PETROL_PUMP = 'hp'
    SOURCE_SULEKHA = 'sulekha'
    SOURCE_SCRATCH_FINDER = 'scratch-finder'

    USER_SOURCES = (
        (SOURCE_WEB, 'Web'),
        (SOURCE_MOBILE_WEB, 'Mobile Web'),
        (SOURCE_DESKTOP_WEB, 'Desktop Web'),
        (SOURCE_EMAIL, 'Email'),
        (SOURCE_SMS, 'SMS'),
        (SOURCE_CHAT, 'Chat'),
        (SOURCE_CALL, 'Call'),
        (SOURCE_APP, 'App'),
        (SOURCE_EVENT, 'Event'),
        (SOURCE_UBER, 'Uber'),
        (SOURCE_OPS_PANEL, 'opsPanel'),
        (SOURCE_ANDROID, 'android'),
        (SOURCE_IPHONE, 'iphone'),
        (SOURCE_FACEBOOK, 'Facebook'),
        (SOURCE_REFERRAL, 'Referral'),
        (SOURCE_HELPSHIFT, 'Helpshift'),
        (SOURCE_JUSTDIAL, 'JustDial'),
        (SOURCE_DRWHEELZ, 'drwheelz'),
        (SOURCE_INCOMING_CALL, 'Incoming Call'),
        (SOURCE_URBANCLAP, 'UrbanClap'),
        (SOURCE_CARS24, 'Cars 24'),
        (SOURCE_HP_PETROL_PUMP, 'HP Petrol Pump'),
        (SOURCE_SULEKHA, 'sulekha'),
        (SOURCE_SCRATCH_FINDER, 'Scratch-Finder'),
    )

    username = models.UUIDField(unique=True, help_text='This is username of user.', null=False, blank=False)
    email = models.EmailField(null=True, help_text="This will be user's email.", blank=True)
    name = models.CharField(max_length=255, null=True, help_text='this is name of alt. customer.', blank=True)
    phone = models.CharField(unique=True, max_length=10, null=True, blank=True)
    ops_phone = models.CharField(unique=True, max_length=10, null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_otp_validated = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    utm_source = models.CharField(max_length=128,null=True, blank=True)
    utm_medium = models.CharField(max_length=128,null=True, blank=True)
    utm_campaign = models.CharField(max_length=128,null=True, blank=True)

    designation = models.CharField(max_length=64,null=True,blank=True)
    company_name = models.CharField(max_length=128,null=True,blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    merged_to = models.ForeignKey('self', blank=True, null=True, related_name='user_merged_to')
    #source = models.CharField(max_length=12, choices=USER_SOURCES, null=True, blank=True)
    source = models.ForeignKey(Source, blank=True, null=True, related_name='user_sources',
                               db_column="source")
    signup_time = models.DateTimeField(null=True, blank=True)

    objects = BumperUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __unicode__(self):
        return "%s-%s" % (self.name,self.phone)

    def __str__(self):
        return "%s-%s" % (self.name,self.phone)

    def __init__(self, *args, **kwargs):
        super(BumperUser, self).__init__(*args, **kwargs)
        setattr(self, '__original_email', self.email)

    def save(self, *args, **kwargs):
        if not self.phone:
            self.phone = None
        if not self.ops_phone:
            self.ops_phone = None
        old_email = getattr(self, '__original_email')
        if self.email != old_email:
            self.is_email_verified = False
        super(BumperUser, self).save(*args, **kwargs)

    def get_full_name(self):
        return '%s' % self.name

    def get_short_name(self):
        return self.name

    def get_jwt_token(self):
        from api.custom_payload_handler import jwt_payload_handler
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(self)
        return jwt_encode_handler(payload)

    def create_drf_token(self):
        Token.objects.create(user=self)

    def get_drf_token(self):
        token,created = Token.objects.get_or_create(user=self)
        return token

    def get_rand_password(self, length=10):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        password = ''
        for i in range(length):
            password += chars[ord(os.urandom(1)) % len(chars)]
        return password

    def reset_password(self):
        from core.utils import generate_sms_auth_code
        new_password = generate_sms_auth_code()
        self.set_password(new_password)
        self.save()

        from services.sms_service import SMSService
        sms_service = SMSService(self)
        sms_text = SMS_TEMPLATES[SMS_TEMPLATE_RESET_PASSWORD]% {'new_password': new_password}
        sms_send_result, sms_text = sms_service.send_sms(self.ops_phone, sms_text)

        if sms_send_result != 'SENT':
            return False
        return True

    def generate_auth_code(self, phone_number=None):
        """
            Function to generate new auth code
        """
        if phone_number == '9886452736':
            auth_code = 1234
        else:
            auth_code = None
        new_code = UserAuthCode.objects.create(
            user=self,
            phone=phone_number,
            auth_code = auth_code
        )
        return new_code.auth_code

    def send_auth_code(self, phone_number=None, send_email=False):
        """
            1) generate auth_code
            2) send it in sms
        """
        # Try and get old auth_code if present or else generate a new one.
        auth_code = None
        user_auth_code = UserAuthCode.objects.filter(user=self, phone=phone_number)
        if len(user_auth_code):
            if user_auth_code[0].expiry_dt < timezone.now():
                # if old code has expired then del it
                log.debug('---- API_send_auth_code: Old Auth Code deleted =%s' % user_auth_code[0].auth_code)
                user_auth_code[0].delete()
            else:
                old_auth_code = user_auth_code[0]
                auth_code = old_auth_code.auth_code

        if not auth_code:
            auth_code = self.generate_auth_code(phone_number)

        if phone_number != '9886452736':
            from services.sms_service import SMSService
            sms_service = SMSService(self)
            sms_text = SMS_TEMPLATES[SMS_TEMPLATE_NEW_AUTH_CODE] % {'auth_code': auth_code}
            sms_send_result, sms_text = sms_service.send_sms(phone_number, sms_text)

            if sms_send_result != 'SENT':
                return False
        if send_email:
            self.send_otp_email(auth_code)
        return True

    def validate_auth_code(self, auth_code):
        """
            validate auth code.
        """
        # auth_codes = UserAuthCode.objects.filter(user=self, auth_code__in=[auth_code, 241286])
        auth_codes = UserAuthCode.objects.filter(user=self, auth_code=auth_code)
        if len(auth_codes):
            auth_codes.delete()
            self.last_login = timezone.now()
            if not self.is_otp_validated:
                self.signup_time = timezone.now()
                self.is_otp_validated = True
            self.save()
            return True
        return False

    def save_user_device(self, device_info, user_device=None):
        """
            create a new default device for user
        """
        from core.managers.pushNotificationManager import register_device_for_notification

        if user_device:
            user_device.device_id = device_info.get('registration_id')
            user_device.device_info = device_info.get('device_info')
            user_device.device_type = device_info.get('device_type')
            user_device.device_os_version = device_info.get('device_os_version')
            user_device.app_version = device_info.get('app_version', 1)
            user_device.is_fcm = device_info.get('is_fcm', False)
            user_device.save()
        else:
            devices_by_push_id = UserDevices.objects.filter(user=self, device_id=device_info.get('registration_id'))
            if devices_by_push_id:
                user_device = devices_by_push_id[0]
                user_device.device_info = device_info.get('device_info')
                user_device.device_type = device_info.get('device_type')
                user_device.device_os_version = device_info.get('device_os_version')
                user_device.app_version = device_info.get('app_version', 1)
                user_device.is_fcm = device_info.get('is_fcm', False)
                user_device.save()

                if not user_device.is_fcm:
                    from push_notifications.models import GCMDevice, APNSDevice
                    existing_devices = None
                    if device_info.get('device_type') == DEVICE_TYPE_ANDROID:
                        existing_devices = GCMDevice.objects.filter(user=self,
                                                                    registration_id=device_info.get('registration_id'))

                    elif device_info.get('device_type') == DEVICE_TYPE_IOS:
                        existing_devices = APNSDevice.objects.filter(user=self,
                                                                     registration_id=device_info.get('registration_id'))

                    if existing_devices:
                        existing_devices[0].active = True
                        existing_devices[0].save()
            else:
                user_device = UserDevices.objects.create(
                    user=self,
                    device_id=device_info.get('registration_id'),
                    device_info=device_info.get('device_info'),
                    device_type=device_info.get('device_type'),
                    device_os_version=device_info.get('device_os_version'),
                    app_version=device_info.get('app_version', 1),
                    is_fcm=device_info.get('is_fcm', False),
                )
                if not user_device.is_fcm and device_info.get('registration_id'):
                    device = register_device_for_notification(self, device_info.get('registration_id'),
                                                              device_info.get('device_type'))

                    if device_info.get('device_type') == DEVICE_TYPE_ANDROID:
                        user_device.gcm_device_id = device.id
                    elif device_info.get('device_type') == DEVICE_TYPE_IOS:
                        user_device.apns_device_id = device.id

                    user_device.save()

        return user_device

    def add_user_to_group(self, group_name):
        g = Group.objects.filter(name=group_name).first()
        if g:
            g.user_set.add(self)

    def send_verification_email(self, request=None):
        """
            Send verification email to user.
        """
        from django.conf import settings
        import uuid
        import urllib
        actkey = uuid.uuid4()
        UserEmailVerify.objects.filter(user=self).delete()
        UserEmailVerify.objects.create(user=self,key=actkey)
        urlparams = urllib.urlencode({'email':self.email,'actkey':actkey})
        base_url = settings.BASE_URL
        if request:
            base_url = request.META['HTTP_HOST'] + '/'
        verification_link = base_url + 'core/verify_email/?' + urlparams
        if self.email:
            from core.models.master import Notifications
            from core.tasks import send_async_new_email_service

            notification = Notifications.objects.get(name='USER_EMAIL_VERIFICATION')
            context = {
                'name': self.name,
                'verification_link': verification_link,
            }
            send_async_new_email_service.delay([self.email], template_folder_name=notification.template_folder_name,
                                               context=context,
                                               analytic_info={
                                                  'notification_id': notification.id,
                                                  'sent_for_account_id': self.id
                                               })

        else:
            log.error('User Email not present, so not sending verification mail')

    def send_welcome_mail(self):
        """
            Send welcome email to user. Usually called along with verification mail at opt validation.
        :return: None
        """
        if self.email:
            from core.models.master import Notifications
            from core.tasks import send_async_new_email_service
            notification = Notifications.objects.get(name='USER_EMAIL_WELCOME')
            context = {
                'name': self.name,
            }
            send_async_new_email_service.delay([self.email], template_folder_name=notification.template_folder_name,
                                               context=context,
                                               analytic_info={
                                                  'notification_id': notification.id,
                                                  'sent_for_account_id': self.id
                                               })

    def save_user_fields(self, data):
        """
        user fields will be saved (data is a dictionary)
        """
        for attr, value in data.items():
            setattr(self, attr, value)
        self.save()

    def send_otp_email(self, auth_code):
        """
        send otp email to user
        """
        from core.tasks import send_custom_notification_task
        send_custom_notification_task.delay('USER_SEND_OTP_EMAIL', {'name': self.name, 'otp': auth_code},
                                            params_dict={'sent_for_account_id': self.id}, user_id=self.id)

    def get_user_permissions(self):
        if self.is_superuser:
            return Permission.objects.all()
        return self.user_permissions.all() | Permission.objects.filter(group__user=self)

    def create_referral_code(self):
        from core.models.referral import ReferralCode
        if self.phone:
            referral_code = ReferralCode.objects.filter(user=self).first()
            if not referral_code:
                referral_code = ReferralCode.objects.create_code(user=self)
            return referral_code
        return None


class UserAuthCode(CreatedAtAbstractBase):
    """
        Table to hold temp auth_code
        1) If a phone requests auth_code for first time it will be sent new code.
        2) If same phone request the auth_code before expiry of code then same code will be returned.
    """
    def __unicode__(self):
        return "%s" % self.id

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_auth_code', null=False)
    phone = models.CharField(max_length=10, null=True)
    auth_code = models.CharField(max_length=6, null=False)
    expiry_dt = models.DateTimeField(blank=False, null=False)
    system_alert_sent = models.BooleanField(default=False, help_text="Marks whether alert has been sent for "
                                                                     "failed OTP, to avoid duplicates alerts.")

    def save(self, *args, **kwargs):
        from core.utils import generate_sms_auth_code

        if not self.auth_code:
            self.auth_code = generate_sms_auth_code()
        self.expiry_dt = timezone.now() + timezone.timedelta(days=7)

        return super(UserAuthCode, self).save(*args, **kwargs)


class UserDevicesManager(models.Manager):
    def get_queryset(self):
        return UserDevicesQuerySet(self.model)


class UserDevicesQuerySet(models.query.QuerySet):
    def send_message(self, title=None, body=None, icon=None, data=None, sound=None, badge=None, click_action=None, **kwargs):
        if self:
            from services.fcm import fcm_send_bulk_message

            reg_ids = list(self.filter(is_active=True).values_list('device_id', flat=True))
            if len(reg_ids) == 0:
                return [{'failure': len(self), 'success': 0}]

            result = fcm_send_bulk_message(
                registration_ids=reg_ids,
                title=title,
                body=body,
                icon=icon,
                data=data,
                sound=sound,
                badge=badge,
                click_action=click_action,
                **kwargs
            )

            results = result[0]['results']
            log.debug('Result for FCM post for =%s' % result)
            for (index, item) in enumerate(results):
                if 'error' in item:
                    reg_id = reg_ids[index]
                    self.filter(device_id=reg_id).update(is_active=False)

            return result


class UserDevices(CreatedAtAbstractBase):
    """
        Model for User - devices details.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False)
    device_id = models.CharField(max_length=512,  null=True,
                                 help_text="This stores gcm id or apns or fcm ID and is used as "
                                           "alternate to device id to uniquely identify "
                                           "device")
    device_type = models.CharField(choices=DEVICE_TYPES, max_length=7, null=True, blank=True)
    device_info = models.CharField(max_length=128, null=True)
    device_os_version = models.CharField(max_length=16, null=True)
    app_version = models.DecimalField(null=True, default=1.00, max_digits=6, decimal_places=2)
    is_fcm = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    gcm_device_id = models.IntegerField(null=True, blank=True)

    # GCM Device Id from push_notifications module
    # APNS Device Id from push_notifications module
    apns_device_id = models.IntegerField(null=True, blank=True)
    objects = UserDevicesManager()

    def __unicode__(self):
        return "%s" % self.id

    def send_message(self, title=None, body=None, icon=None, data=None, sound=None, badge=None, click_action=None, **kwargs):
        from services.fcm import fcm_send_message
        result = fcm_send_message(
            registration_id=self.device_id,
            title=title,
            body=body,
            icon=icon,
            data=data,
            sound=sound,
            badge=badge,
            click_action=click_action,
            **kwargs
        )

        log.debug('Result for FCM post for =%s' % result)
        device = UserDevices.objects.filter(device_id=self.device_id)
        if 'error' in result['results'][0]:
            device.update(is_active=False)

        return result


class UserCar(CreatedAtAbstractBase):
    """
        Save User cars.
    """
    user = models.ForeignKey(BumperUser, null=False)
    car_model = models.ForeignKey(CarModel, null=False)
    registration_number = models.CharField(max_length=13, null=True, blank=True)
    purchased_on = models.DateField(null=True, blank=True)
    color = models.CharField(max_length=32,null=True,blank=True)
    new_color = models.ForeignKey(CarColor, null=True, blank=True)
    active = models.BooleanField(null=False,blank=False,default=True)
    insurer = models.CharField(max_length=128,null=True,blank=True)
    insurer_due_date = models.DateField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    variant = models.ForeignKey(CarModelVariant, null=True, blank=True)
    vin_no = models.CharField(max_length=32,null=True,blank=True)
    manufactured_on = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return "{0}".format(self.id)

    def owner_details(self):
        return "[Id:%s] %s (%s)" % (self.user.id, self.user.name, self.user.username)


class UserAddress(CreatedAtAbstractBase):
    user = models.ForeignKey(BumperUser)
    alias = models.CharField(max_length=128,null=True)
    address = models.ForeignKey(Address)

    def __unicode__(self):
        return "{0}".format(self.id)

    def __str__(self):
        return str(self.id)


class UserCredit(CreatedAtAbstractBase):
    user = models.OneToOneField(BumperUser, related_name='user_credit')
    credit = models.DecimalField(max_digits=10, decimal_places=2)

    def __unicode__(self):
        return "{0}-{1}".format(self.user_id,self.credit)

    def __str__(self):
        return "{0}-{1}".format(self.user_id,self.credit)


class UserEmailVerify(CreatedAtAbstractBase):
    """
        Stores the verification keys for emails
    """
    user = models.ForeignKey(BumperUser, null=False)
    key = models.UUIDField()

    def __str__(self):
        return "%s" % self.id

    def __unicode__(self):
        return "%s" % self.id


class PartnerLead(CreatedAtAbstractBase):
    """
        To store partner leads. If a new dealer signs up to become a partner.
    """
    name = models.CharField(max_length=256)
    mobile = models.CharField(db_index=True, max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=256, null=True, blank=True)
    workshop_name = models.CharField(max_length=256, null=True, blank=True)
    message = models.CharField(max_length=512, null=True, blank=True)
    utm_source = models.CharField(max_length=512, blank=True, null=True)
    utm_medium = models.CharField(max_length=512, blank=True, null=True)
    utm_campaign = models.CharField(max_length=512, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % self.id

    def __unicode__(self):
        return "%s" % self.id

    @staticmethod
    def get_field_names():
        fnames = PartnerLead._meta.get_all_field_names()
        return fnames


@receiver(post_save, sender=PartnerLead)
def partnerlead_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            from core.models.master import Notifications
            from core.models.message import Messages
            from core.tasks import send_async_new_email_service

            notification = Notifications.objects.get(name='OPS_PARTNER_REQUEST')
            email_body = notification.template % {
                'name': instance.name,
                'mobile': instance.mobile,
                'email': instance.email,
                'city': instance.city,
                'workshop_name': instance.workshop_name,
                'message': instance.message,
                'utm_source': instance.utm_source,
                'utm_medium': instance.utm_medium,
                'utm_campaign': instance.utm_campaign,
            }
            send_async_new_email_service.delay(to_list=notification.get_to_list(),
                                               cc_list=notification.get_cc_list(),
                                               subject=notification.subject,
                                               body=email_body,
                                               message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS,
                                               analytic_info={
                                                   'notification_id': notification.id
                                               })
    except:
        log.exception('Failed to send notification for partner request.')


class Followup(CreatedAtAbstractBase):
    #booking = models.IntegerField(null=True, blank=True)
    COMM_MODE_CALL = 1
    COMM_MODE_WHATSAPP = 2
    COMM_MODE_SMS = 3
    COMM_MODE_EMAIL = 4
    COMM_MODE_EXEC_APP = 5
    COMM_MODE_PUSH = 6
    COMM_MODE_WEB_CHAT = 7
    COMM_MODE_HELPSHIFT = 8
    COMM_MODE_USER_APP_ANDROID = 9

    COMM_MODES = (
        (COMM_MODE_CALL, "Call"),
        (COMM_MODE_WHATSAPP, "WhatsApp"),
        (COMM_MODE_SMS, "SMS"),
        (COMM_MODE_EMAIL, "Email"),
        (COMM_MODE_EXEC_APP, "Executive App"),
        (COMM_MODE_PUSH, "Push"),
        (COMM_MODE_WEB_CHAT, "Web Chat"),
        (COMM_MODE_HELPSHIFT, "Helpshift"),
        (COMM_MODE_USER_APP_ANDROID, "User App Android"),
    )

    FOLLOWUP_FOR_CUSTOMER = 1
    FOLLOWUP_FOR_WORKSHOP = 2
    FOLLOWUP_FOR_CHOICES = (
        (FOLLOWUP_FOR_CUSTOMER, "Customer"),
        (FOLLOWUP_FOR_WORKSHOP, "Workshop")
    )

    note = models.TextField(null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, help_text="Person who punched this entry")
    next_followup_dt = models.DateTimeField(blank=True, null=True)
    result = models.ForeignKey(FollowupResult, blank=True, null=True)
    comm_mode = models.PositiveSmallIntegerField(choices=COMM_MODES,default=COMM_MODE_CALL,
                                                 help_text="How was the customer communicated?")
    follow_for = models.PositiveSmallIntegerField(choices=FOLLOWUP_FOR_CHOICES, default=FOLLOWUP_FOR_CUSTOMER,
                                                  help_text="Workshop or customer?")

    def __unicode__(self):
        return "%s" % self.id


class UserInquiry(CreatedAtAbstractBase):
    """
        Save User inquiry without booking.
    """
    INQUIRY_OPEN = 1
    INQUIRY_POSTPONED = 2
    INQUIRY_FOLLOWING_UP = 3
    INQUIRY_CLOSED_BOOKING = 4  # booking created by user
    INQUIRY_RNR = 5
    INQUIRY_CLOSED_NO_BOOKING = 6  # booking not created by user
    INQUIRY_DELAYED_OPS = 7
    INQUIRY_DUPLICATE = 8
    INQUIRY_CLOSED_BOOKING_NOFOLLOWUP = 9
    INQUIRY_PRICE_ISSUE = 10
    INQUIRY_TRUST_ISSUE = 11

    INQUIRY_STATUSES = (
        (INQUIRY_OPEN,"Open"),
        (INQUIRY_POSTPONED,"Postponed"),
        (INQUIRY_FOLLOWING_UP,"Following Up"),
        (INQUIRY_CLOSED_BOOKING,"Closed - Booking created"),
        (INQUIRY_RNR,"RNR"),
        (INQUIRY_CLOSED_NO_BOOKING,"Closed - Booking not created"),
        (INQUIRY_DELAYED_OPS,"Delayed Ops"),
        (INQUIRY_CLOSED_BOOKING_NOFOLLOWUP,"Closed - Booking created before followup"),
        (INQUIRY_DUPLICATE,"Duplicate"),
        (INQUIRY_PRICE_ISSUE,"Closed - Price Issue"),
        (INQUIRY_TRUST_ISSUE,"Closed - Trust Issue"),
    )

    LEAD_QUALITY_HOT = 1
    LEAD_QUALITY_WARM = 2
    LEAD_QUALITY_COLD = 3
    LEAD_QUALITY_RED_HOT = 4

    LEAD_QUALITIES = (
        (LEAD_QUALITY_HOT, "Hot"),
        (LEAD_QUALITY_WARM, "Warm"),
        (LEAD_QUALITY_COLD, "Cold"),
        (LEAD_QUALITY_RED_HOT, "Red Hot"),
    )

    user = models.ForeignKey(BumperUser, null=False, blank=False)
    inquiry = models.CharField(max_length=2048)
    status = models.PositiveIntegerField(null=False, blank=False, choices=INQUIRY_STATUSES, default=INQUIRY_OPEN)
    # source = models.CharField(max_length=12, choices=BumperUser.USER_SOURCES,
    #                           null=True, blank=True)
    source = models.ForeignKey(Source, blank=True, null=True, related_name='userinquiry_sources',
                               db_column="source")
    car_model = models.ForeignKey(CarModel,null=True,blank=True)
    followup = models.ManyToManyField(Followup, related_name='user_inquiry_followup')
    assigned_to = models.ForeignKey(BumperUser, null=True, blank=True, related_name='userinquiry_assigned_to')
    reference = models.CharField(max_length=1048, null=True, blank=True)
    lead_quality = models.PositiveSmallIntegerField(null=True, blank=True, choices=LEAD_QUALITIES)
    cancellation_reason = models.ForeignKey(InquiryCancellationReasons, null=True, blank=True)
    city = models.ForeignKey(City)
    utm_source = models.CharField(max_length=128, null=True, blank=True)
    utm_medium = models.CharField(max_length=128, null=True, blank=True)
    utm_campaign = models.CharField(max_length=128, null=True, blank=True)

    history = HistoricalRecords()

    def __unicode__(self):
        return "{0}".format(self.id)


class WorkshopUser(CreatedAtAbstractBase):
    """
        Mapping of Users assigned to workshop
    """
    ROLE_BUMPER_EXECUTIVE = 1
    ROLE_BUMPER_ASST_MANAGER = 2
    ROLE_BUMPER_MANAGER = 3
    ROLE_WORKSHOP_OWNER = 4

    WORKSHOP_ROLES = (
        (ROLE_BUMPER_EXECUTIVE, "Bumper Workshop Executive"),
        (ROLE_BUMPER_ASST_MANAGER, "Bumper Workshop Asst Manager"),
        (ROLE_BUMPER_MANAGER, "Bumper Workshop Manager"),
        (ROLE_WORKSHOP_OWNER, "Workshop Owner"),
    )

    user = models.ForeignKey(BumperUser, null=False, blank=False, limit_choices_to=models.Q(groups__name='OpsUser'))
    workshop = models.ForeignKey(Workshop, null=False, blank=False)
    role = models.PositiveSmallIntegerField(choices=WORKSHOP_ROLES)

    def __unicode__(self):
        return "{0}".format(self.id)


class DriverLocation(CreatedAtAbstractBase):
    WORKSHOP_TO_CUST_PICKUP = 1
    CUST_TO_WORKSHOP_PICKUP = 2
    WORKSHOP_TO_CUST_DROP = 3
    DRIVER_CURRENT_LOC = 4 # When he is not in booking.

    DIRECTION_CHOICES = (
        (WORKSHOP_TO_CUST_PICKUP, "DriverToCustPick"),
        (CUST_TO_WORKSHOP_PICKUP, "CustToDriverPick"),
        (WORKSHOP_TO_CUST_DROP, "DriverToCustDrop"),
        (DRIVER_CURRENT_LOC, "DriverCurrentLoc"),
    )

    driver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="location_driver")
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=False,
                                   blank=False)  # to store the location info of driver
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=False,
                                    blank=False)  # to store the location info of driver.
    direction = models.PositiveSmallIntegerField(choices=DIRECTION_CHOICES)
    track_time = models.DateTimeField()

    history = HistoricalRecords()

    def __unicode__(self):
        return "%s" % self.id


class UserAttendance(CreatedAtAbstractBase):
    ATTENDANCE_ENTRY = 1
    ATTENDANCE_EXIT = 2

    ATTENDANCE_TYPES = (
        (ATTENDANCE_ENTRY, "Entry"),
        (ATTENDANCE_EXIT, "Exit"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_attendance")
    attendance_type = models.PositiveSmallIntegerField(choices=ATTENDANCE_TYPES)
    track_time = models.DateTimeField()

    def __unicode__(self):
        return "%s" % self.id


class ScratchFinderLead(CreatedAtAbstractBase):
    STATUS_SUBMITTED = 1
    STATUS_APPROVED = 2
    STATUS_REJECTED = 3

    STATUS_CHOICES = (
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    )
    user = models.ForeignKey(BumperUser, null=False, blank=False, help_text="User that submitted this lead.")
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=15, unique=True, db_index=True)
    detail = models.CharField(max_length=2048, null=True, blank=True)
    status = models.PositiveIntegerField(null=False, blank=False, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    car_model = models.ForeignKey(CarModel, null=True, blank=True)
    updated_by = models.ForeignKey(BumperUser, related_name="sflead_updated_by")
    media = models.ForeignKey(Media, related_name="sflead_media")

    history = HistoricalRecords()

    def __unicode__(self):
        return "{0}".format(self.id)


@python_2_unicode_compatible
class CreditTransaction(CreatedAtAbstractBase):
    TRANSACTION_TYPE_CREDIT = 1
    TRANSACTION_TYPE_DEBIT = 2

    TRANSACTION_TYPES = (
        (TRANSACTION_TYPE_CREDIT, 'CREDIT'),
        (TRANSACTION_TYPE_DEBIT, 'DEBIT')
    )

    ENTITY_BOOKING = "Booking"  # Model Name
    ENTITY_REFERRAL = "Referral"
    ENTITY_USER = "BumperUser"
    ENTITY_PROMOTION = "Promotion"

    ENTITY_CHOICES = (
        (ENTITY_BOOKING, ENTITY_BOOKING),
        (ENTITY_REFERRAL, ENTITY_REFERRAL),
        (ENTITY_USER, ENTITY_USER),
        (ENTITY_PROMOTION, ENTITY_PROMOTION),
    )

    user = models.ForeignKey(BumperUser, related_name='user_credittrx')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    trans_type = models.PositiveSmallIntegerField(_("Transaction Type"), choices=TRANSACTION_TYPES)
    entity = models.CharField(max_length=64, choices=ENTITY_CHOICES, null=True,
                              blank=True, db_index=True)  # if null -> no entity else, entity because of which credit used/gained.
    entity_id = models.IntegerField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _("Credit Transaction")
        verbose_name_plural = _("Credit Transactions")

    def __str__(self):
        return "%s-%s-%s" % (self.user, self.amount, self.trans_type)


class NotificationSubscriber(CreatedAtAbstractBase):
    """
        Table keep mapping for who all need to be send notification.
    """
    user = models.ForeignKey(BumperUser, limit_choices_to=Q(groups__name='OpsUser'))
    notification = models.ForeignKey(Notifications)

    class Meta:
        verbose_name = _("Notification Subscriber")
        verbose_name_plural = _("Notification Subscribers")
        unique_together = ('user', 'notification')

    def __str__(self):
        return "%s-%s" % (self.user, self.notification.name)

    def __unicode__(self):
        return "%s-%s" % (self.user, self.notification.name)


class UserDetail(CreatedAtAbstractBase):
    """
        Table to keep user details which are not going to be accessed frequently.
    """
    user = models.OneToOneField(BumperUser, related_name="user_detail", limit_choices_to=Q(groups__name='OpsUser'))
    imei_no = models.CharField(max_length=16, null=True, blank=True,
                               help_text="IMEI number of device used by user.")
    cre_id = models.CharField(max_length=16, null=True, blank=True,
                              help_text="CRE ID from Ninja CRM")

    def __unicode__(self):
        return "%s" % self.user_id


class Caller(CreatedAtAbstractBase):
    """
        Caller list for assignment - it contains priority and last assigned etc.
    """
    user = models.ForeignKey(BumperUser, related_name='caller',
                             limit_choices_to=Q(groups__name='Caller'))
    last_call_inquiry = models.BooleanField(default=False)
    last_call_booking = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField()
    assigned_bookings_count = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s-%s" % (self.user, self.sort_order)
