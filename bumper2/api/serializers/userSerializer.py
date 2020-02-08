from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.models import Group
from django.db.models import Prefetch
from core.models.master import City, CarModel, Source
from core.models.common import Address, Media
from core.models.incentive import IncentiveEvent
from core.models.booking import UserVendorCash, Booking
from core.models.users import (
    UserCar,
    UserAddress,
    UserCredit,
    PartnerLead,
    UserInquiry,
    UserDevices,
    Followup,
    WorkshopUser,
    DriverLocation,
    UserAttendance,
    ScratchFinderLead,
    UserDetail,
    CreditTransaction
)
from core.models.referral import ReferralCode, ReferralCampaign, Referral
from masterSerializers import CitySerializer, CarModelSerializer, FollowupResultSerializer, WorkshopSerializer
from commonSerializers import AddressSerializer, DynamicFieldsModelSerializer, MediaSerializer
from django.utils import six, timezone
import re
from core.constants import DEVICE_TYPES
from core.managers import userManager
from core.tasks import send_custom_notification_task
import logging
logger = logging.getLogger(__name__)


def build_pretty_errors(errors):
    pretty = []
    for key in errors:
        pretty.append(', '.join(errors[key]))
    if pretty:
        return {'status': '\n'.join(pretty)}
    return {}


class PhoneNumberField(serializers.Field):
    """
        Phone number validation to be consistent
    """
    default_error_messages = {
        'incorrect_type': 'Incorrect type. Expected a string, but got {input_type}',
        'incorrect_format': 'Incorrect format. Expected 10 digit phone number.',
        'out_of_range': 'Value out of range. Expected 10 digit phone number.'
    }

    def to_representation(self, obj):
        return str(obj)

    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            self.fail('incorrect_type', input_type=type(data).__name__)

        # match_reg = re.compile(r'^[+]?((\d+[\s]?[-]?\d+)+)$')
        match_reg = re.compile(r'^\d{10}$')
        if not match_reg.match(data):
            self.fail('incorrect_format')

        if len(str(data)) != 10 :
            self.fail('out_of_range')

        return data


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class UserCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCredit
        fields = ('credit',)
        read_only_fields = ('credit',)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ('__all__')


class UserSerializer(DynamicFieldsModelSerializer):
    city = CitySerializer(remove_fields=['is_denting_active','state','is_wash_active','active'],read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source='city', write_only=True, allow_null=False, required=False)
    groups = GroupSerializer(many=True, required=False, read_only=True)
    user_credit = UserCreditSerializer(required=False, read_only=True)
    active_devices = serializers.SerializerMethodField()
    user_detail = UserDetailSerializer(required=False, read_only=True)
    referral_code = serializers.SlugRelatedField(queryset=ReferralCode.objects.all(), slug_field='code__iexact',
                                                 required=False, write_only=True)
    referral = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id','name','phone','email','city','designation','company_name',
                  'city_id','groups','ops_phone','user_credit','is_email_verified','date_joined','source',
                  'active_devices', 'user_detail', 'referral_code', 'referral')
        read_only_fields = ('groups','user_credit','is_email_verified','date_joined', 'ops_phone','active_devices',
                            'user_detail')

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        is_admin = self.context.get('is_admin')
        if not is_admin:
            self.fields.pop('active_devices',[])

    def get_active_devices(self, obj):
        return UserDeviceSerializer(userManager.get_user_active_devices(obj), many=True).data

    def get_referral(self, obj):
        referral = Referral.objects.filter(referred=obj).select_related('referrer').first()
        if referral:
            return {"referrer": UserSerializer(referral.referrer, new_fields=['name']).data}
        else:
            return None

    def update(self, instance, validated_data):
        send_email = False
        request = self.context.get('request')
        if validated_data.get('email') and validated_data.get('email') != instance.email:
            validated_data['is_email_verified'] = False
            send_email = True
        if validated_data.get('city') and validated_data.get('city') != instance.city:
            # Cancel all the bookings before pickup scheduled (status flow num = 3).
            Booking.objects.filter(user=instance,
                                   status__flow_order_num__lt=3).update(status_id=24,
                                                                        cancel_reason_dd_id=51,
                                                                        reason_for_cancellation_desc="User changed city")
        userManager.handle_referral_code(instance, validated_data)
        new_instance = super(UserSerializer, self).update(instance, validated_data)
        if send_email:
            new_instance.send_verification_email(request=request)
        return new_instance


class UserCarSerializer(DynamicFieldsModelSerializer):
    car_model = CarModelSerializer(read_only=True, remove_fields=['colors', 'variants'])
    car_model_id = serializers.PrimaryKeyRelatedField(
                    queryset=CarModel.objects.all(), source='car_model')
    user_id = serializers.PrimaryKeyRelatedField(
                    queryset=get_user_model().objects.all(), source='user', write_only=True, required=False)
    active_bookings = serializers.SerializerMethodField()

    class Meta:
        model = UserCar
        fields = ('id', 'registration_number', 'purchased_on', 'color',
                  'active', 'car_model_id', 'car_model', 'insurer', 'year',
                  'insurer_due_date', 'user_id', 'active_bookings', 'vin_no', 'manufactured_on',
                  'variant', 'new_color')
        #read_only_fields = ('user')

    def get_active_bookings(self, obj):
        b_list = []
        if hasattr(obj, 'bookings'):
            for b in obj.bookings:
                b_list.append(b.id)
        return b_list

    def update(self, instance, validated_data):
        from core.managers import bookingManager
        #request = self.context.get('request')
        year = validated_data.get('year')
        if year and year != instance.year:
            car_model = instance.car_model
            new_car_model = car_model.get_car_model_by_year(year)
            if new_car_model != car_model:
                bookings = Booking.objects.filter(usercar=instance)
                bookings = bookingManager.filter_open_booking(bookings)
                if bookings.count() > 0:
                    raise serializers.ValidationError('Year cannot be changed. There are active bookings on the car.')
                instance.active = False
                instance.save()
                instance.pk = None
                instance.year = year
                instance.active = True
                instance.car_model = new_car_model
                instance.save()
        new_instance = super(UserCarSerializer, self).update(instance, validated_data)
        return new_instance

    @property
    def errors(self):
        ugly_errors = super(UserCarSerializer, self).errors
        pretty_errors = build_pretty_errors(ugly_errors)
        return ReturnDict(pretty_errors, serializer=self)


class SendAuthCodeSerializer(serializers.Serializer):
    phone = PhoneNumberField(required=True)
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    device_type = serializers.ChoiceField(choices=DEVICE_TYPES, required=True)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(),
                                                 source='city', write_only=True, allow_null=False)
    app_version = serializers.FloatField(required=False)
    device_info = serializers.JSONField(required=False)
    device_os_version = serializers.CharField(max_length=16, required=False)
    registration_id = serializers.CharField(max_length=512, required=False)
    utm_source = serializers.CharField(max_length=128, required=False)
    utm_medium = serializers.CharField(max_length=128, required=False)
    utm_campaign = serializers.CharField(max_length=128, required=False)
    source = serializers.ChoiceField(choices=Source.objects.all(), required=False)
    is_scratch_finder = serializers.BooleanField(default=False, required=False, write_only=True)
    referral_code = serializers.SlugRelatedField(queryset=ReferralCode.objects.all(), slug_field='code__iexact',
                                                 required=False, write_only=True)

    def __init__(self, *args, **kwargs):
        super(SendAuthCodeSerializer, self).__init__(*args, **kwargs)
        self.fields['referral_code'].error_messages['does_not_exist'] = 'Referral Code - {value} is not valid'

    @property
    def errors(self):
        ugly_errors = super(SendAuthCodeSerializer, self).errors
        pretty_errors = build_pretty_errors(ugly_errors)
        return ReturnDict(pretty_errors, serializer=self)


class ValidateAuthCodeSerializer(serializers.Serializer):
    auth_code = serializers.IntegerField(required=True, max_value=9999, min_value=1000)
    phone = PhoneNumberField(required=True)
    event_code = serializers.CharField(required=False, max_length=128)


class PhoneNumberSerializer(serializers.Serializer):
    phone = PhoneNumberField(required=True)
    is_scratch_finder = serializers.BooleanField(default=False, required=False, write_only=True)


class UserAddressSerializer(DynamicFieldsModelSerializer):
    address = AddressSerializer(remove_fields=['id'])
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(),
                                              required=False)

    class Meta:
        model = UserAddress
        fields = ('__all__')

    @classmethod
    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('address')
        return queryset

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address_obj = Address.objects.create(**address_data)
        ua = UserAddress.objects.create(address=address_obj, **validated_data)
        return ua

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address')
        address_obj = instance.address
        address_obj.__dict__.update(**address_data)
        address_obj.save()
        #address_obj = Address.objects.create(**address_data)
        #ua = UserAddress.objects.create(address=address_obj, **validated_data)
        instance.__dict__.update(**validated_data)
        instance.save()
        return instance


class SavePushRegSerializer(serializers.Serializer):
    app_version = serializers.FloatField(required=False)
    device_info = serializers.JSONField(required=False)
    device_os_version = serializers.CharField(max_length=16, required=False)
    registration_id = serializers.CharField(max_length=512, required=True)
    device_type = serializers.ChoiceField(choices=DEVICE_TYPES, required=True)
    is_fcm = serializers.BooleanField(required=False, default=False)


class AuthSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=254)
    password = serializers.CharField(max_length=254)


class UTMFieldSerializer(serializers.Serializer):
    utm_source = serializers.CharField(max_length=128,required=False)
    utm_medium = serializers.CharField(max_length=128,required=False)
    utm_campaign = serializers.CharField(max_length=128,required=False)


class PartnerLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerLead
        fields = ('name','email','mobile','city','workshop_name','message','utm_source','utm_medium','utm_campaign')


class FollowupSerializer(serializers.ModelSerializer):
    updated_by = UserSerializer(read_only=True,
                                new_fields=['name','ops_phone'])
    result_details = FollowupResultSerializer(source='result', read_only=True)

    class Meta:
        model = Followup
        fields = ('__all__')


class UserInquirySerializer(DynamicFieldsModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
         queryset=get_user_model().objects.all(), source='user', write_only=True, required=False)
    user = UserSerializer(read_only=True,new_fields=['name','phone'])
    car_model = CarModelSerializer(read_only=True, remove_fields=['colors', 'variants'])
    car_model_id = serializers.PrimaryKeyRelatedField(
          queryset=CarModel.objects.all(), source='car_model', write_only=True, required=False)
    followup = FollowupSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = UserInquiry
        fields = ('__all__')

    def __init__(self, *args, **kwargs):
        # self.fields.pop('followup')
        super(UserInquirySerializer, self).__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        followup = validated_data.pop('followup', None)
        return super(UserInquirySerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        followup = validated_data.pop('followup', None)
        updated_by = validated_data.pop('updated_by', None)
        instance = super(UserInquirySerializer, self).create(validated_data)
        if followup:
            data = {"followup": followup, "updated_by": updated_by}
            userManager.update_followup(instance, data)
        from core.tasks import send_user_inquiry_to_ops
        send_user_inquiry_to_ops.delay(instance.id)
        from core.tasks import send_custom_notification_task
        send_custom_notification_task.delay('USER_INQUIRY_NOTIFICATION',{'user_name': instance.user.name }, user_id=instance.user_id)
        return instance


class UserDeviceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = UserDevices
        fields = ('device_type', 'device_info', 'device_os_version', 'app_version')


class UserInquiryFollowupSerializer(DynamicFieldsModelSerializer):
    followup = FollowupSerializer(many=True)
    class Meta:
        model = UserInquiry
        fields = ('id','followup','assigned_to')

    def update(self, instance, validated_data):
        return userManager.update_followup(instance, validated_data)

    def save(self, **kwargs):
        request = self.context.get('request')
        kwargs['updated_by'] = request.user
        super(UserInquiryFollowupSerializer, self).save(**kwargs)

    @classmethod
    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(Prefetch(
                                                    'followup',
                                                    Followup.objects.order_by('-created_at').select_related('updated_by',
                                                                                                            'result'),
                                            ))
        return queryset


class MarketingCampaignSerializer(serializers.Serializer):
    media = serializers.FileField(write_only=True)
    phone = PhoneNumberField(required=True)
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)


class ChatUserSerializer(serializers.Serializer):
    phone = PhoneNumberField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(required=False)


class WorkshopUserSerializer(DynamicFieldsModelSerializer):
    workshop_details = WorkshopSerializer(read_only=True, source='workshop')
    user_details = UserSerializer(read_only=True, source='user',
                                  remove_fields=['groups','user_credit','city','active_devices','user_detail',
                                                 'referral'])
    class Meta:
        model = WorkshopUser
        fields = '__all__'


class DriverLocationSerializer(serializers.ModelSerializer):
    driver = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                queryset=get_user_model().objects.all())
    class Meta:
        model = DriverLocation
        fields = '__all__'

    def create(self, validated_data):
        return userManager.add_driver_location(validated_data)


class UserAttendanceSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                queryset=get_user_model().objects.all())
    class Meta:
        model = UserAttendance
        fields = '__all__'


class ScratchFinderLeadSerializer(serializers.ModelSerializer):
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                    queryset=get_user_model().objects.all())
    user = serializers.PrimaryKeyRelatedField(default=serializers.CreateOnlyDefault(serializers.CurrentUserDefault()),
                                              queryset=get_user_model().objects.all())
    media = MediaSerializer(remove_fields=['media_type', 'desc'])
    car_model_details = CarModelSerializer(source='car_model', read_only=True,
                                           remove_fields=['colors', 'variants'])

    class Meta:
        model = ScratchFinderLead
        fields = '__all__'

    # def validate_phone(self, value):
    #     User = get_user_model()
    #     if User.objects.filter(phone=value).exists():
    #         raise serializers.ValidationError('This phone number already exists in our system.')
    #     return value

    def create(self, validated_data):
        try:
            with transaction.atomic():
                m = validated_data.pop('media')
                if not m.get('file'):
                    m['file'] = m.pop('image_name')
                media = Media.objects.create(**m)
                validated_data['media'] = media
                instance = super(ScratchFinderLeadSerializer, self).create(validated_data)

                # create incentives if any
                incentive_data = {"name": "INCENTIVE_EVENT_SFLEAD_CREATE",
                                  "entity": UserVendorCash.ENTITY_SFLEAD,
                                  "entity_id": instance.id,
                                  "promise_info": "Scratch Finder Lead Created.",
                                  "user": validated_data.get('user')
                                  }
                userManager.handle_incentive_events(incentive_data)

                # send notifications
                send_custom_notification_task.delay('USER_SMS_SCRATCH_LEAD_CREATED',
                                                    {},
                                                    user_id=instance.user_id)

                # Send promo message only if user not exist in our system already.
                User = get_user_model()
                if not User.objects.filter(phone=instance.phone).exists():
                    if instance.car_model:
                        send_custom_notification_task.delay('USER_SMS_SCRATCH_LEAD_PROMO1',
                                                            {'user_name': instance.user.name,
                                                             'lead_name': instance.name,
                                                             'car_model': instance.car_model.name},
                                                            params_dict={'phone': instance.phone})

                    send_custom_notification_task.apply_async(('USER_SMS_SCRATCH_LEAD_PROMO2',
                                                              {}),
                                                              {"params_dict": {'phone': instance.phone}},
                                                              countdown=7200)
                return instance
        except:
            # may need to send trigger to dev about issue.
            logger.exception("SF Lead not created.")
            raise serializers.ValidationError("Not able to create lead.")

    def update(self, instance, validated_data):
        lead_approved = False
        if validated_data.get('status') == ScratchFinderLead.STATUS_APPROVED:
            lead_approved = True
        new_instance = super(ScratchFinderLeadSerializer, self).update(instance, validated_data)
        create_event = IncentiveEvent.objects.filter(name="INCENTIVE_EVENT_SFLEAD_CREATE").first()
        if create_event and lead_approved:
            uvc = UserVendorCash.objects.filter(entity=UserVendorCash.ENTITY_SFLEAD, entity_id=instance.id,
                                                event=create_event).first()
            if uvc:
                # send notifications
                approved_event = IncentiveEvent.objects.filter(name="INCENTIVE_EVENT_SFLEAD_APPROVED").first()
                if approved_event:
                    send_custom_notification_task.delay('USER_SMS_SCRATCH_LEAD_APPROVED',
                                                        {'amount': uvc.amount,
                                                         'approved_amount': approved_event.tp_cash},
                                                        user_id=instance.user_id)
        if lead_approved:
            incentive_data = {"name": "INCENTIVE_EVENT_SFLEAD_APPROVED",
                              "entity": UserVendorCash.ENTITY_SFLEAD,
                              "entity_id": instance.id,
                              "promise_info": "Scratch Finder Lead Approved.",
                              "user": new_instance.user,
                              "promise_and_transfer": True}
            userManager.handle_incentive_events(incentive_data)

        if validated_data.get('status') == ScratchFinderLead.STATUS_REJECTED:
            send_custom_notification_task.delay('USER_SMS_SCRATCH_LEAD_REJECTED',
                                                {},
                                                user_id=instance.user_id)

        return new_instance


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = '__all__'


class ReferralCampaignSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ReferralCampaign
        fields = '__all__'


class CreditTransactionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = '__all__'


class CancelledBookingFollowupSerializer(serializers.Serializer):
    followup = FollowupSerializer(many=True)
    next_followup = serializers.DateTimeField(required=True)
