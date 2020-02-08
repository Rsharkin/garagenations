from django.db.models import Prefetch, Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from core.models.incentive import IncentiveEvent
from core.models.users import UserAddress, UserDevices, UserCar, DriverLocation, CreditTransaction, UserCredit
from core.models.booking import Booking, UserVendorCash
from core.models.referral import ReferralCode, Referral, ReferralCampaign
from core.tasks import send_custom_notification_task
from django.conf import settings
import logging
logger = logging.getLogger('__name__')


# This is for creating a user without any authentication from APP.
def create_user(data):
    User = get_user_model()
    user = User.objects.create_user(**data)
    return user


def find_matching_users_by_phone(phone):
    """
        To find matching users by phone
    :param phone:
    :return:
    """
    User = get_user_model()
    matching_users = User.objects.filter(phone=phone)
    return matching_users[0] if matching_users else False


def find_matching_users_by_email(email):
    """
        To find matching users by email
    :param email:
    :return:
    """
    User = get_user_model()
    matching_users = User.objects.filter(email=email)
    return matching_users[0] if matching_users else False


def find_matching_users(email=None, phone=None):
    """
        To find matching users
    :param email: 
    :param phone: 
    :return: 
    """
    if not email and not phone:
        return False

    if email:
        matching_user = find_matching_users_by_email(email)
        if matching_user:
            return matching_user

    if phone:
        matching_user = find_matching_users_by_phone(phone)
        if matching_user:
            return matching_user

    return False

def merge_new_user_to_existing(existing_user, new_user):
    # merging the new user and old user:
    # 1. Marking old car inactive and change user of new usercar
    # 2. Change user to old one in new booking id.
    # 3. May be add some identification on new user (that it was merged into which old user) - merged_to
    # 4. change user to old one in new user address.
    # 5. change user to old one in new user devices.
    #    a) get new devices
    #    b) get existing devices having same device id
    #    c) get the gcm and apns ids of existing devices
    #    d) delete gcm and apns devices
    #    e) delete existing devices having same device id
    #    f) update existing user on new devices.
    new_bookings = Booking.objects.filter(user=new_user)
    if new_bookings:
        #if existing user has any booking with flow_order_num >=3 and <=21 then keep the existing one and cancel the new one
        #else cancel the existing one and keep the new one
        existing_bookings = Booking.objects.filter(user=existing_user, status__flow_order_num__gte=3,
                                                   status__flow_order_num__lte=21)
        if existing_bookings:
            for booking in new_bookings:
                booking.status_id=24
                booking.user=existing_user
                booking.save()
                # usercar = booking.usercar
                # usercar.user = existing_user
                # usercar.save()
                # need to know if inactive the new car or not.
        else:
            Booking.objects.filter(user=existing_user).exclude(status_id__in=[22,25,23,24]).update(status_id=24)
            new_bookings.update(user=existing_user)
            # for booking in new_bookings:
            #     booking.user=existing_user
            #     booking.save()
                # usercar = booking.usercar
                # usercar.user = existing_user
                # usercar.save()
            #new_bookings.update(user=existing_user)
    UserCar.objects.filter(user=new_user).update(user=existing_user)

    UserAddress.objects.filter(user=new_user).update(user=existing_user)

    new_devices = UserDevices.objects.filter(user=new_user)
    if new_devices:
        from push_notifications.models import GCMDevice, APNSDevice
        new_device_id_list = []
        for device in new_devices:
            if device.device_id is not None:
                new_device_id_list.append(device.device_id)
        existing_common_devices = UserDevices.objects.filter(user=existing_user,device_id__in=new_device_id_list)
        if existing_common_devices:
            gcm_id_list = []
            apns_id_list = []
            for device in existing_common_devices:
                if device.gcm_device_id:
                    gcm_id_list.append(device.gcm_device_id)
                elif device.apns_device_id:
                    apns_id_list.append(device.apns_device_id)
            if gcm_id_list:
                GCMDevice.objects.filter(id__in=gcm_id_list).delete()
            if apns_id_list:
                APNSDevice.objects.filter(id__in=apns_id_list).delete()
            existing_common_devices.delete()
        new_devices.update(user=existing_user)
        GCMDevice.objects.filter(user=new_user).update(user=existing_user)
        APNSDevice.objects.filter(user=new_user).update(user=existing_user)

    if existing_user.city != new_user.city and new_user.city:
        existing_user.city = new_user.city
        existing_user.save()
    new_user.merged_to = existing_user
    new_user.save()


def get_usercar_queryset(user):
    if user.groups.filter(name='OpsUser').exists():
        queryset = UserCar.objects.all()
    else:
        queryset = UserCar.objects.filter(user=user)
    bookings = Booking.objects.all()
    from core.managers.bookingManager import filter_open_booking

    return queryset.select_related('car_model__brand').prefetch_related(Prefetch(
                                                                       "booking_set",
                                                                        queryset=filter_open_booking(bookings),
                                                                        to_attr='bookings'
                                                                        )).order_by('-active','-created_at')


def get_user_active_devices(user):
    # Get user devices
    return UserDevices.objects.filter(user=user, device_id__isnull=False)\
        .exclude(gcm_device_id__isnull=False, apns_device_id__isnull=False)


def update_followup(instance, validated_data):
    followup = validated_data.pop('followup',[])
    updated_by = validated_data.pop('updated_by', None)

    from core.tasks import send_custom_notification_task

    for f in followup:
        f['updated_by'] = updated_by
        tags = f.pop('tags',None)
        followup_obj = instance.followup.create(**f)
        if tags:
            followup_obj.tags.add(*tags)
        result = f.get('result')
        if result and result.notification:
            notification = result.notification
            send_custom_notification_task.delay(notification.name,
                                                {'instance_id': instance.id,
                                                 'result_name': result.name,
                                                 'followup_for_type': 'Inquiry'
                                                 })

    is_instance_updated = False
    for attr, value in validated_data.items():
        if not isinstance(value, (list,dict)):
            is_instance_updated = True
            setattr(instance, attr, value)

    if is_instance_updated:
        instance.updated_by = updated_by
        instance.save()

    return instance


def add_driver_location(validated_data):
    driver = validated_data.get('driver')
    direction = validated_data.get('direction')
    driver_location = DriverLocation.objects.filter(driver=driver, direction=direction).first()
    if driver_location:
        driver_location.track_time = validated_data.get('track_time')
        driver_location.latitude = validated_data.get('latitude')
        driver_location.longitude = validated_data.get('longitude')
        driver_location.save()
    else:
        driver_location = DriverLocation.objects.create(**validated_data)
    return driver_location


def send_paytm_cash(phone_num, amount, tx_info, request_type="NULL", try_again=True):
    import time
    import paytm_checksum
    import requests
    import json
    import uuid
    from collections import OrderedDict


    #application_type = "application/json"
    currentTime = int(round(time.time() * 1000))
    MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
    nonce = currentTime

    request_data1 = OrderedDict([("request", OrderedDict([("requestType", request_type),
                                                        ("merchantGuid", settings.PAYTM_MERCHANT_ID),
                                                        ("merchantOrderId", str(uuid.uuid4())),
                                                        ("salesWalletName", "BUMPER.COM"),
                                                        ("salesWalletGuid", settings.PAYTM_SALES_WALLET_GUID),
                                                        ("payeeEmailId", ""),
                                                        ("payeePhoneNumber", phone_num),
                                                        ("payeeSsoId", ""),
                                                        ("appliedToNewUsers", "Y"),
                                                        ("amount", str(amount)), ("currencyCode", "INR")])),
                              ("metadata", str(tx_info)),
                              ("ipAddress", "127.0.0.1"),
                              ("platformName", "PayTM"),
                              ("operationType", "SALES_TO_USER_CREDIT")])

    requestData = json.dumps(request_data1)
    logger.info("PayTM data: {}".format(request_data1))

    checksum = paytm_checksum.generate_checksum_by_str(requestData, MERCHANT_KEY)
    hmacHeaders = {
            'Content-Type':'application/json',
            'mid': settings.PAYTM_MERCHANT_ID,
            'checksumhash' : checksum
    }

    r = requests.post(settings.PAYTM_BASE_URL+'/wallet-web/salesToUserCredit', json=request_data1, headers=hmacHeaders)
    logger.info("Paytm response: {}".format(r.json()))
    if r.status_code == 200:
        response = r.json()
        if response.get('status') == 'SUCCESS':
            return True, r.json()
        elif try_again:
            send_paytm_cash(phone_num, amount, tx_info, try_again=False)
        else:
            logger.error("To Phone: {} Paytm Response Failure: {}".format(phone_num, r.json()))
    return False, r.json()


def handle_incentive_events(data):
    # create vendor cash
    transferred = data.get('transferred', False)
    promise_and_transfer = data.get('promise_and_transfer', False)
    user = data.get('user')
    entity = data.get('entity')
    entity_id = data.get('entity_id')
    event = IncentiveEvent.objects.filter(name=data.get('name'),
                                          active=True).filter(Q(expiry_date__lte=timezone.localtime(timezone.now())) |
                                                              Q(expiry_date__isnull=True)).first()
    # Two type of events - promised and transferred.
    # if transferred is False - then promised
    # if transferred is True - then this is to be transferred.
    # incase of transferred, need to get event and if it is not already transferred, transfer it.
    uvc = None
    if event and event.tp_cash:
        if transferred or promise_and_transfer:
            if promise_and_transfer:
                uvc = UserVendorCash.objects.create(user=user, event=event,
                                                    amount=event.tp_cash, entity=entity,
                                                    entity_id=entity_id,
                                                    promise_info=data.get('promise_info'))
                uvc_list = [uvc]
            else:
                uvc_list = UserVendorCash.objects.filter(user=user, event=event,
                                                         entity=entity, entity_id=entity_id,
                                                         transferred=False)
            for uvc in uvc_list:
                # transfer money to paytm
                tx_info = {'entity':entity, 'entity_id':entity_id, 'event_name':event.name,
                           'user_name': user.name}
                is_success, settle_info = send_paytm_cash(user.phone, event.tp_cash, tx_info)
                uvc.transferred = True
                uvc.transfer_info = data.get('transfer_info')
                # If paytm returns with success
                if is_success:
                    uvc.settled = True
                    uvc.settle_info = str(settle_info)
                else:
                    uvc.tx_data = str(settle_info)
                uvc.save()
        else:
            uvc = UserVendorCash.objects.create(user=user, event=event,
                                                amount=event.tp_cash, entity=entity,
                                                entity_id=entity_id,
                                                promise_info=data.get('promise_info'))
    if event and event.credit:
        if promise_and_transfer:
            reason = data.get('name') + " - " + data.get('promise_info')
            add_user_credits(user, event.credit, entity, entity_id, reason, allow_multiple=True)
    return uvc


def add_user_credits(user, credit, entity, entity_id, reason, allow_multiple=False):
    ct = None
    if not allow_multiple:
        ct = CreditTransaction.objects.filter(user=user,
                                              trans_type=CreditTransaction.TRANSACTION_TYPE_CREDIT,
                                              entity=entity,
                                              entity_id=entity_id).first()
    if not ct:
        with transaction.atomic():
            CreditTransaction.objects.create(user=user, amount=credit,
                                             trans_type=CreditTransaction.TRANSACTION_TYPE_CREDIT,
                                             entity=entity,
                                             entity_id=entity_id, reason=reason)
            uc, created = UserCredit.objects.get_or_create(user=user, defaults={"credit": 0})
            uc.credit += credit
            uc.save()
            logger.info(
                "Credits Added - entity-{}, entity_id-{}, User-{}, Reason-{}".format(
                    entity,
                    entity_id,
                    user.id,
                    reason))
    else:
        logger.info(
            "No Credits Added - User already got credits before. entity-{}, entity_id-{}, User-{}, Reason-{}".format(
                entity,
                entity_id,
                user.id,
                ct.reason))


def handle_referral_campaign(flow_name, referral):
    campaign = ReferralCampaign.objects.filter(name=flow_name, active=True).first()
    user_id = None
    amount = None
    if campaign:
        if campaign.referrer_credit:
            add_user_credits(referral.referrer, campaign.referrer_credit,
                             CreditTransaction.ENTITY_REFERRAL, referral.id, campaign.name)
            user_id = referral.referrer_id
            amount = campaign.referrer_credit
        elif campaign.referred_credit:
            add_user_credits(referral.referred, campaign.referred_credit,
                             CreditTransaction.ENTITY_REFERRAL, referral.id, campaign.name)
            user_id = referral.referred_id
            amount = campaign.referred_credit
        notifications = campaign.notifications.all()
        for notification in notifications:
            send_custom_notification_task.delay(notification.name,
                                                {'amount': amount,
                                                 'referrer_name': referral.referrer.name,
                                                 'referred_name': referral.referred.name,
                                                 },
                                                user_id=user_id)


def handle_referral_code(user, data):
    code = data.get('referral_code')
    if code:
        referral_code = ReferralCode.objects.filter(code=code).first()
        if referral_code:
            referral = Referral.objects.filter(referred=user).first()
            if not referral:
                referral = Referral.objects.create(referrer=referral_code.user, referred=user)
                flow_name = "CREATE_USER"
                handle_referral_campaign(flow_name, referral)
