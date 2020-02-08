import decimal
import logging
from datetime import datetime, time
from fractions import gcd

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, Max, Count
from django.forms.models import model_to_dict
from django.utils import timezone
from rest_framework import serializers

from core import constants
from core.models import Workshop, WorkshopHoliday
from core.models.booking import (
    BookingAddress,
    BookingAlertTriggerStatus,
    BookingPackage,
    Booking,
    BookingPackagePanel,
    BookingImage,
    BookingInvoice,
    BookingDiscount,
    BookingCoupon,
    BookingProformaInvoice,
    BookingReworkPackage,
    BookingReworkPackagePanel,
    BookingQualityChecks,
    EntityChangeTracker,
    BookingHandoverItem,
    BookingChecklist
)
from core.models.common import Address, Media
from core.models.coupons import Coupon
from core.models.master import BookingStatus, BookingOpsStatus, Package, PackagePrice
from core.models.payment import Payment
from core.models.users import UserAddress, CreditTransaction
from core.utils import build_s3_path, build_local_path
from core.utils import format_datetime_for_grid, handle_car_pickup_incentive, handle_car_pickup_referral
from services.email_service import NewEmailService

logger = logging.getLogger(__name__)


def strip_decimals(o):
    if type(o) == decimal.Decimal:
        return str(o)
    elif type(o) == list:
        return map(strip_decimals, o)
    elif type(o) == dict:
        return dict([(k, strip_decimals(v)) for k, v in o.iteritems()])
    else:
        return o


def get_pickup_slots(data):
    # If required select only workshops which supports brand of car.
    current_time = timezone.localtime(timezone.now())
    end_range = 8
    slots = []
    if current_time.hour >= 18:
        slots.append({"date":str(current_time.date()),"slots" :[]})
        current_time = current_time + timezone.timedelta(days=1)
        current_time = current_time.replace(hour=10,minute=0,second=0,microsecond=0)
        end_range = 7
    elif current_time.hour <= 7:
        current_time = current_time.replace(hour=10,minute=0,second=0,microsecond=0)
    else:
        # current_time.hour >= 8 and current_time.hour < 18
        current_time = current_time.replace(hour=current_time.hour+3,microsecond=0)

    current_time = current_time.replace(tzinfo=None)
    workshops = Workshop.objects.filter(is_doorstep=data.get('is_doorstep', False),
                                        active=True, city=data.get('city', 1))

    for _ in range(1, end_range):
        curdate = current_time.date()
        day = current_time.weekday()
        start_time,end_time = None,None
        for workshop in workshops:
            off_days = workshop.off_days if workshop.off_days else ''
            if str(day) in off_days:
                continue
            wh = WorkshopHoliday.objects.filter(workshop=workshop, holiday_date=curdate, active=True)
            if wh:
                continue
            open_at = datetime.combine(curdate,workshop.open_at)
            close_at = datetime.combine(curdate,workshop.close_at)
            if start_time:
                if current_time < open_at < start_time:
                    start_time = open_at
            elif close_at > current_time:
                if open_at > current_time:
                    start_time = open_at
                else:
                    start_time = current_time
            if end_time:
                if close_at > end_time > current_time:
                    end_time = close_at
            elif close_at > current_time:
                end_time = close_at
        curdate_slots = []
        if start_time and end_time:
            sdatetime = round_time(dt=start_time,roundTo=60*60)
            edatetime = sdatetime + timezone.timedelta(hours=1)
            end_datetime = end_time
            while edatetime <= end_datetime:
                curdate_slots.append({"start_time":sdatetime.time(), "end_time":edatetime.time()})
                sdatetime = edatetime
                edatetime = edatetime + timezone.timedelta(hours=1)
        slots.append({"date":str(curdate),"slots" :curdate_slots})
        current_time = current_time.replace(hour=0,minute=0,second=0)
        current_time = current_time + timezone.timedelta(days=1)
    return slots


def round_time(dt, roundTo=60):
    if dt.minute or dt.second:
        minutes = roundTo/60
        return dt + timezone.timedelta(minutes=minutes - dt.minute % minutes,
                                       seconds=-(dt.second % 60))
    else:
        return dt


def get_drop_slots(data):
    # If required select only workshops which supports brand of car.
    current_time = timezone.localtime(timezone.now())
    hours_after_booking = 2
    current_time = current_time + timezone.timedelta(hours=hours_after_booking)
    current_time = current_time.replace(tzinfo=None)
    slots = []
    for _ in range(0,2):
        curdate = current_time.date()
        day = current_time.weekday()
        start_time,end_time = datetime.combine(curdate,time(9,0,0)),datetime.combine(curdate,time(20,0,0))
        if start_time < current_time:
            start_time = current_time
        if end_time < current_time:
            current_time = current_time.replace(hour=0,minute=0,second=0)
            current_time = current_time + timezone.timedelta(days=1)
            continue
        curdate_slots = []
        if start_time:
            sdatetime = round_time(dt=start_time,roundTo=60*60)
            edatetime = sdatetime + timezone.timedelta(hours=2)
            end_datetime = end_time
            while edatetime <= end_datetime:
                curdate_slots.append({"start_time":sdatetime.time().replace(microsecond=0), "end_time":edatetime.time().replace(microsecond=0)})
                sdatetime = edatetime
                edatetime = edatetime + timezone.timedelta(hours=2)
        slots.append({"date":str(curdate),"slots" :curdate_slots})
        current_time = current_time.replace(hour=0,minute=0,second=0)
        current_time = current_time + timezone.timedelta(days=1)
    return slots


def save_booking_address(validated_data):
    useraddress_id = validated_data.pop('useraddress_id')
    booking = validated_data.get('booking')
    useraddress_obj = UserAddress.objects.filter(id=useraddress_id,user=booking.user).first()
    if not useraddress_obj:
        raise serializers.ValidationError("User Address does not exist.")
    address_data = model_to_dict(useraddress_obj.address)
    del address_data['id']
    address_type = validated_data.get('type')
    ba = BookingAddress.objects.filter(booking=validated_data.get('booking'),type=address_type).first()
    if ba:
        address = ba.address
        for attr, value in address_data.items():
            if not isinstance(value, (list,dict)):
                setattr(address, attr, value)
        address.save()
        ba.useraddress = useraddress_obj
        ba.save()
    else:
        address_obj = Address.objects.create(**address_data)
        ba = BookingAddress.objects.create(address=address_obj, useraddress=useraddress_obj, **validated_data)
    return ba


def get_status_from_action(action):
    status = None
    ops_status = None
    if action:
        status = BookingStatus.objects.filter(id=constants.ACTION_DICT[action]['status']).first()
        if constants.ACTION_DICT[action].get('ops_status') is not False:
            ops_status = BookingOpsStatus.objects.filter(id=constants.ACTION_DICT[action]['ops_status']).first()
        else:
            ops_status = False
    return status, ops_status


def process_booking_alert_notification(booking, alert_type):
    # notification = Notifications.objects.get(name=notification_type)
    notification = alert_type.notification

    # There are lot of unneccessary processing happens here. Need to make it better.

    bill_amt = ''
    bill_details = get_bill_details_new(booking)
    if bill_details and bill_details.get('total_amt'):
        bill_amt = bill_details.get('total_amt')

    booking_packages = BookingPackage.objects.filter(booking=booking)
    package_taken = []
    for item in booking_packages:
        package_taken.append(item.package.package.name)

    pickup_time = format_datetime_for_grid(booking.pickup_time)
    drop_time = format_datetime_for_grid(booking.drop_time)
    pickup_address = booking.booking_address.filter(type=BookingAddress.ADDRESS_TYPE_PICKUP).first()
    drop_address = booking.booking_address.filter(type=BookingAddress.ADDRESS_TYPE_DROP).first()

    context = {
        'booking_id': booking.id,
        'car_model': booking.usercar.car_model,
        'pickup_driver_name': booking.pickup_driver.name if booking.pickup_driver else '',
        'pickup_driver_phone': booking.pickup_driver.ops_phone if booking.pickup_driver else '',
        'drop_driver_name': booking.drop_driver.name if booking.drop_driver else '',
        'drop_driver_phone': booking.drop_driver.ops_phone if booking.drop_driver else '',
        'cc_num': settings.BUMPER_SUPPORT_NUM,  # customer care bumper
        'bill_amount': bill_amt,
        'package_details': ', '.join(package_taken),
        'pickup_details': pickup_time if pickup_time else '',
        'drop_time': drop_time if drop_time else '',
        'customer_name': booking.user.name,
        'customer_phone': booking.user.phone,
        'current_status': booking.status.status_desc if booking.status else '',
        'current_ops_status': booking.ops_status.ops_status_desc if booking.ops_status else '',
        'pickup_address': pickup_address.address.address1 if pickup_address else '',
        'drop_address': drop_address.address.address1 if drop_address else '',
    }

    email_format = 'html'
    cc_address_list = notification.get_cc_list()
    to_address_list = notification.get_to_list()

    email_service = NewEmailService(to_list=to_address_list, cc_list=cc_address_list, email_format=email_format,
                                    context=context,
                                    analytic_info={
                                        'booking_id': booking.id,
                                        'notification_id': notification.id,
                                        'sent_for_account_id': booking.user.id,
                                    })
    email_service.send(email_body=str(notification.template), subject=notification.subject)

    BookingAlertTriggerStatus.objects.create(
        booking=booking,
        is_triggered=True,
        alert_type=alert_type
    )


def get_bill_details_wo_invoice(booking_obj):
    """
    to get price with tax for a booking.
    if separate tax is True, then tax will be calculated separately
    otherwise it will be included in price and taxes will be 0.
    """
    booking_packages = booking_obj.booking_package.all()
    total_labour_price = decimal.Decimal('0.00')
    total_part_price = decimal.Decimal('0.00')
    total_material_price = decimal.Decimal('0.00')
    total_service_tax = decimal.Decimal('0.00')
    total_kk_tax = decimal.Decimal('0.00')
    total_sb_tax = decimal.Decimal('0.00')
    total_vat = decimal.Decimal('0.00')
    total_igst = decimal.Decimal('0.00')
    total_cgst = decimal.Decimal('0.00')
    total_sgst = decimal.Decimal('0.00')
    total_gst = decimal.Decimal('0.00')
    editable = False
    for bp in booking_packages:
        if bp.package.package.category == Package.CATEGORY_DENT:
            booking_package_panels = bp.booking_package_panel.all()
            for bpp in booking_package_panels:
                if bpp.panel.editable or bpp.panel.internal:
                    editable = True
                total_labour_price += get_booking_package_panel_labour_price(bpp)
                total_part_price += get_booking_package_panel_part_price(bpp)
                total_material_price += get_booking_package_panel_material_price(bpp)
        else:
            if bp.package.package.internal:
                editable = True
            total_labour_price += get_booking_package_labour_price(bp)
            total_part_price += get_booking_package_part_price(bp)
            total_material_price += get_booking_package_material_price(bp)

    # total_service_tax = (constants.SERVICE_TAX_FACTOR * total_labour_price).quantize(constants.TWO_PLACES)
    # total_kk_tax = (constants.KK_TAX_FACTOR * total_labour_price).quantize(constants.TWO_PLACES)
    # total_sb_tax = (constants.SB_TAX_FACTOR * total_labour_price).quantize(constants.TWO_PLACES)
    # total_vat = (constants.VAT_FACTOR * (total_part_price + total_material_price)).quantize(constants.TWO_PLACES)

    total_amt = total_part_price + total_material_price + total_labour_price
    if booking_obj.created_at.date() >= datetime.strptime('25082017', "%d%m%Y").date():
        total_cgst = (total_amt * constants.CGST_FACTOR / decimal.Decimal('100.00')).quantize(constants.TWO_PLACES)
        total_sgst = (total_amt * constants.SGST_FACTOR / decimal.Decimal('100.00')).quantize(constants.TWO_PLACES)
        total_gst = total_cgst + total_sgst
    return {
        "total_amt":total_amt,
        "total_service_tax":total_service_tax,
        "total_kk_tax":total_kk_tax,
        "total_sb_tax":total_sb_tax,
        "total_vat":total_vat,
        "total_cgst":total_cgst,
        "total_sgst":total_sgst,
        "total_igst":total_igst,
        "total_gst":total_gst,
        "editable":editable,
        "total_part_price":total_part_price,
        "total_material_price":total_material_price,
        "total_labour_price":total_labour_price
    }


def get_ratio(numbers):
    denominater = reduce(gcd,numbers)
    ratio = [i/denominater for i in numbers]
    return ratio


def get_coupon_discount(booking,coupon):
    # check if booking packages and coupon package has anything. If not coupon is useless and is not allowed to add.
    discounted_bps = booking.booking_package.filter(package__package__in=coupon.packages.all()) # filter may not work if prefetch
    if discounted_bps:
        # based on common package - get price sum of all such packages (later get sum of part/material/labour based on coupon allowed).
        part_amt_for_calc = decimal.Decimal('0.0')
        material_amt_for_calc = decimal.Decimal('0.0')
        labour_amt_for_calc = decimal.Decimal('0.0')

        for bp in discounted_bps:
            # We are considering tax also for discounting for now.
            if str(Coupon.COUPON_APPLICATION_PART) in coupon.applicable_to:
                if bp.package.package.category == Package.CATEGORY_DENT:
                    for panel in bp.booking_package_panel.all():
                        part_amt_for_calc += get_booking_package_panel_part_price(panel)
                else:
                    part_amt_for_calc += get_booking_package_part_price(bp)
            if str(Coupon.COUPON_APPLICATION_LABOUR) in coupon.applicable_to:
                if bp.package.package.category == Package.CATEGORY_DENT:
                    for panel in bp.booking_package_panel.all():
                        labour_amt_for_calc += get_booking_package_panel_labour_price(panel)
                else:
                    labour_amt_for_calc += get_booking_package_labour_price(bp)
            if str(Coupon.COUPON_APPLICATION_MATERIAL) in coupon.applicable_to:
                if bp.package.package.category == Package.CATEGORY_DENT:
                    for panel in bp.booking_package_panel.all():
                        material_amt_for_calc += get_booking_package_panel_material_price(panel)
                else:
                    material_amt_for_calc += get_booking_package_material_price(bp)
    else:
        return {}

    coupon_discount = 0
    part_coupon_disc = decimal.Decimal('0.0')
    material_coupon_disc = decimal.Decimal('0.0')
    labour_coupon_disc = decimal.Decimal('0.0')
    cashback_discount = decimal.Decimal('0.0')
    # get discount dictionary (consider percentage, cashback everything)
    total_amt_for_calc = part_amt_for_calc + material_amt_for_calc + labour_amt_for_calc

    if total_amt_for_calc <= 0:
        return {}

    if coupon.value > 0:
        if coupon.type == Coupon.COUPON_TYPE_MONETORY:
            coupon_value = coupon.value
            if total_amt_for_calc < coupon.value:
                coupon_value = total_amt_for_calc
            # price_ratio = get_ratio([int(part_amt_for_calc*100),int(material_amt_for_calc*100),int(labour_amt_for_calc*100)])
            # total_sum = sum(price_ratio)
            # part_coupon_disc = decimal.Decimal(price_ratio[0]) * decimal.Decimal(coupon_value) / total_sum
            # material_coupon_disc = decimal.Decimal(price_ratio[1]) * decimal.Decimal(coupon_value) / total_sum
            # labour_coupon_disc = decimal.Decimal(price_ratio[2]) * decimal.Decimal(coupon_value) / total_sum
        else:
            coupon_value = total_amt_for_calc * decimal.Decimal(coupon.value) / decimal.Decimal('100.00')
            if coupon.amount_limit and coupon.amount_limit < coupon_value:
                coupon_value = coupon.amount_limit

        coupon_value = decimal.Decimal(coupon_value).to_integral_exact(rounding=decimal.ROUND_CEILING)
        price_ratio = get_ratio([int(part_amt_for_calc*100),int(material_amt_for_calc*100),int(labour_amt_for_calc*100)])
        total_sum = sum(price_ratio)
        part_coupon_disc = (decimal.Decimal(price_ratio[0]) * decimal.Decimal(coupon_value) / total_sum).quantize(constants.TWO_PLACES)
        material_coupon_disc = (decimal.Decimal(price_ratio[1]) * decimal.Decimal(coupon_value) / total_sum).quantize(constants.TWO_PLACES)
        labour_coupon_disc = (decimal.Decimal(price_ratio[2]) * decimal.Decimal(coupon_value) / total_sum).quantize(constants.TWO_PLACES)
            # else:
            #     part_coupon_disc = decimal.Decimal(part_amt_for_calc) * decimal.Decimal(coupon.value) / decimal.Decimal('100.00')
            #     material_coupon_disc = decimal.Decimal(material_amt_for_calc) * decimal.Decimal(coupon.value) / decimal.Decimal('100.00')
            #     labour_coupon_disc = decimal.Decimal(labour_amt_for_calc) * decimal.Decimal(coupon.value) / decimal.Decimal('100.00')

        # part_coupon_disc = part_coupon_disc.quantize(constants.TWO_PLACES)
        # material_coupon_disc = material_coupon_disc.quantize(constants.TWO_PLACES)
        # labour_coupon_disc = labour_coupon_disc.quantize(constants.TWO_PLACES)

        coupon_discount = part_coupon_disc + material_coupon_disc + labour_coupon_disc
    if coupon.cashback_value > 0:
        if coupon.cashback_type == Coupon.COUPON_TYPE_MONETORY:
            cashback_discount = coupon.cashback_value
        else:
            cashback_discount = (total_amt_for_calc * decimal.Decimal(coupon.cashback_value) / decimal.Decimal('100.00')).quantize(constants.TWO_PLACES)
        cashback_discount = min(cashback_discount,coupon.cashback_amt_limit) if coupon.cashback_amt_limit else cashback_discount
        if cashback_discount > total_amt_for_calc:
            cashback_discount = total_amt_for_calc

    return {
        'coupon_discount' : coupon_discount,
        'cashback_discount' : cashback_discount,
        'part_coupon_disc': part_coupon_disc,
        'material_coupon_disc': material_coupon_disc,
        'labour_coupon_disc': labour_coupon_disc
    }


def get_coupon_details(booking, coupon_code):
    coupon = Coupon.objects.filter(code=coupon_code.upper(), campaign__city=booking.city).first()
    message = ""
    discount_dict = {}
    if coupon and not coupon.expired(booking):
        coupon_used_count = BookingCoupon.objects.filter(booking__user=booking.user, coupon=coupon).count()
        total_used_count = BookingCoupon.objects.filter(coupon=coupon).count()
        booking_coupon_count = BookingCoupon.objects.filter(booking=booking).count()
        if ((coupon.used_times > 0 and coupon_used_count < coupon.used_times) or coupon.used_times == 0) and \
                ((coupon.max_use > 0 and total_used_count < coupon.max_use) or coupon.max_use == 0) and \
                booking_coupon_count == 0:
            discount_dict = get_coupon_discount(booking,coupon)
            if not discount_dict:
                # add the packages which are added in coupon.
                logger.debug('---- Method_get_coupon_details: Coupon not allowed for added booking packages')
                message = "Coupon not allowed for added booking packages"
        else:
            logger.debug('---- Method_get_coupon_details: Coupon already used.')
            message = "Coupon already used."
    else:
        logger.debug('---- Method_get_coupon_details: Invalid Coupon Code')
        message = "Invalid Coupon Code"
    return discount_dict, message, coupon


def get_bill_with_coupon(booking, coupon_code):
    discount_dict,message,coupon = get_coupon_details(booking,coupon_code)
    bill_dict = get_bill_details_new(booking)
    bill_dict['discount_dict'] = discount_dict
    bill_dict['payable_amt'] = str(decimal.Decimal(bill_dict['payable_amt']) -
                                   discount_dict.get('coupon_discount', decimal.Decimal('0.0')))
    return bill_dict, message, coupon


def adjust_amt_for_rework_booking(booking, rework_booking, usercar):
    old_invoice = BookingInvoice.objects.filter(booking=rework_booking,
                                                status=BookingInvoice.INVOICE_STATUS_PENDING).first()

    if old_invoice:
        success_payments = Payment.objects.filter(invoice=old_invoice,
                                                  tx_status=Payment.TX_STATUS_SUCCESS)

        total_payment = decimal.Decimal('0.00')
        for payment in success_payments:
            if payment.tx_type == Payment.TX_TYPE_PAYMENT:
                total_payment += payment.amount
            else:
                total_payment -= payment.amount

        part_amt_for_calc = old_invoice.part_price
        material_amt_for_calc = old_invoice.material_price
        labour_amt_for_calc = old_invoice.labour_price

        new_sum = old_invoice.payable_amt - total_payment

        if new_sum > 0:
            price_ratio = get_ratio(
                [int(part_amt_for_calc * 100), int(material_amt_for_calc * 100), int(labour_amt_for_calc * 100)])
            total_sum = sum(price_ratio)
            new_part_price = (decimal.Decimal(price_ratio[0]) * decimal.Decimal(new_sum) / total_sum).quantize(
                constants.TWO_PLACES)
            new_material_price = (decimal.Decimal(price_ratio[1]) * decimal.Decimal(new_sum) / total_sum).quantize(
                constants.TWO_PLACES)
            new_labour_price = (decimal.Decimal(price_ratio[2]) * decimal.Decimal(new_sum) / total_sum).quantize(
                constants.TWO_PLACES)

            pp = PackagePrice.objects.filter(package__category=Package.CATEGORY_ADV_PAYMENT_TO,
                                             car_type=usercar.car_model.car_type).first()
            if pp:
                BookingPackage.objects.create(booking=rework_booking, package=pp,
                                              labour_price=-new_labour_price,
                                              material_price=-new_material_price,
                                              part_price=-new_part_price)

            pp = PackagePrice.objects.filter(package__category=Package.CATEGORY_ADV_PAYMENT_FROM,
                                             car_type=usercar.car_model.car_type).first()
            if pp:
                BookingPackage.objects.create(booking=booking, package=pp,
                                              labour_price=new_labour_price,
                                              material_price=new_material_price,
                                              part_price=new_part_price)

            save_invoice(rework_booking)


def create_booking(validated_data):
    booking_package = validated_data.pop("booking_package", [])
    usercar = validated_data.get("usercar")
    user = validated_data.get("user")
    device_type = validated_data.pop('device_type',None)
    action = validated_data.pop("action", 1)
    status,ops_status = get_status_from_action(action)
    validated_data['status'] = status
    validated_data['ops_status'] = ops_status
    city = validated_data.get("city")
    rework_booking = validated_data.get("rework_booking")
    #if rework_booking and rework_booking.status_id != 22:
    #    logger.info("Create Rework Booking -- Old booking not car delivered:- booking id:%s" % rework_booking.id)
    #    raise serializers.ValidationError("Old booking not car delivered. Cannot create rework booking.")
    if not city:
        if not user.city:
            raise serializers.ValidationError("User does not have city.")
        validated_data['city'] = user.city
    if user != usercar.user:
        logger.info("Create Booking -- Usercar does not belong to User:- User:%s, Usercar:%s" % (user, usercar))
        raise serializers.ValidationError("UserCar does not belong to User")

    booking = Booking.objects.create(**validated_data)

    if rework_booking and usercar:
        adjust_amt_for_rework_booking(booking, rework_booking, usercar)
        if rework_booking.status.flow_order_num < 22:
            update_booking(rework_booking, {'action': 22})
            update_booking(rework_booking, {'action': 25})

    # TODO: if rework booking add all package/panel prices to 0 (if not marked extra)
    for bp in booking_package:
        bp["booking"] = booking
        bp_panels = bp.pop('booking_package_panel',[])
        bp['price'] = bp.pop('manual_price',None)
        extra = bp.get('extra')
        if booking.rework_booking_id is not None and not extra:
            bp['part_price'] = 0
            bp['material_price'] = 0
            bp['labour_price'] = 0
        bp_obj = BookingPackage.objects.create(**bp)
        if bp_obj.package.package.category == Package.CATEGORY_DENT:
            for bp_panel in bp_panels:
                extra = bp_panel.get('extra')
                if booking.rework_booking_id is not None and not extra:
                    bp_panel['part_price'] = 0
                    bp_panel['material_price'] = 0
                    bp_panel['labour_price'] = 0
                BookingPackagePanel.objects.create(booking_package=bp_obj,**bp_panel)
    return booking


def validate_proforma_invoice(validated_data):
    booking = validated_data.get('booking')
    existing_invoice = BookingProformaInvoice.objects.filter(booking=booking,
                                                             status=BookingProformaInvoice.INVOICE_STATUS_PENDING)
    if existing_invoice:
        raise serializers.ValidationError("Pending Proforma Invoice exists.")


def create_qc_checks(booking, validated_data):
    bqc = []
    checked_items = validated_data.get('checked_items', [])
    group_num = 1
    if checked_items:
        group_num_dict = BookingQualityChecks.objects.filter(booking=booking).aggregate(Max('group_num'))
        group_num = group_num_dict.get('group_num__max', 1)
        if group_num:
            group_num += 1
    for item in checked_items:
        if not item.get('updated_by'):
            item['updated_by'] = validated_data.get('updated_by')
        item['group_num'] = group_num
        bqc.append(BookingQualityChecks(booking=booking, **item))

    try:
        if bqc:
            BookingQualityChecks.objects.bulk_create(bqc)
    except:
        raise serializers.ValidationError("Error in creating Quality checks.")


def create_handover_list(booking, validated_data):
    bqc = []
    for item in validated_data.get('item_list', []):
        if not item.get('updated_by'):
            item['updated_by'] = validated_data.get('updated_by')
        item['status'] = booking.status
        item['ops_status'] = booking.ops_status
        bqc.append(BookingHandoverItem(booking=booking, **item))

    try:
        if bqc:
            BookingHandoverItem.objects.bulk_create(bqc)
    except Exception as e:
        raise serializers.ValidationError("Error in creating Handover list")


def create_checklist(booking, validated_data):
    # item_list is the bookingchecklist object list (It is not checklist item list)
    item_list = validated_data.get('item_list', [])
    if item_list:
        group_num_list = BookingChecklist.objects.filter(
                                            booking=booking).select_related(
                                                'item__category').values(
                                                    'item__category').annotate(Max('group_num'))
        group_num_dict = {}
        for gdict in group_num_list:
            group_num_dict[gdict['item__category']] = gdict['group_num__max']

        checkitem_list = [checkitem.get('item') for checkitem in item_list]
        benchmark_list = BookingChecklist.objects.filter(booking=booking, group_num=1, item__in=checkitem_list)
        benchmark_dict = {}
        for row in benchmark_list:
            benchmark_dict[row.item_id] = row

        # workshop qc list (last qc) for not allowing car to go out of workshop at status (drop driver ready to go)
        latest_workshop_qc_dict = None
        if booking.status_id == 19 and booking.ops_status_id == 3:
            qc_group_max = group_num_dict.get(7)
            if qc_group_max:
                latest_workshop_qc_list = BookingChecklist.objects.filter(booking=booking, group_num=qc_group_max,
                                                                          item__category_id=7)
                latest_workshop_qc_dict = {}
                for row in latest_workshop_qc_list:
                    latest_workshop_qc_dict[row.item_id] = row
        try:
            with transaction.atomic():
                is_qc_failed = False
                bc_objs = []
                ThroughModel = BookingChecklist.media.through
                through_list = []
                bc_dict = {}
                #bc_list = []
                for item in item_list:
                    if not item.get('updated_by'):
                        item['updated_by'] = validated_data.get('updated_by')
                    item['status'] = booking.status
                    item['ops_status'] = booking.ops_status
                    checklist_item = item.get('item')
                    item['group_num'] = group_num_dict.get(checklist_item.category_id, 0) + 1
                    media_list = item.pop('media', [])
                    # do not allow update if photo mandatory
                    if checklist_item.photo_mandatory and not media_list:
                        logger.error("Error in creating checklist - Photo is mandatory :booking_id: %s, item_id:%s",
                                     booking.id, checklist_item.id)
                        raise serializers.ValidationError("Error in creating checklist.")
                    if not item.get('is_applicable', True):
                        item['has_issue'] = False
                    # compare item with benchmark group if not 1st group
                    if item.get('group_num') > 1:
                        benchitem = benchmark_dict.get(checklist_item.id)
                        if benchitem and (
                                        item.get('is_applicable', True) != benchitem.is_applicable or
                                        item.get('has_issue', False) != benchitem.has_issue):
                            item['mismatch'] = True
                            if latest_workshop_qc_dict and checklist_item.category_id != 7:
                                is_qc_failed = True

                    # if qc is not matching with previous then change the status to qc failed.
                    if latest_workshop_qc_dict:
                        workshop_qc_item = latest_workshop_qc_dict.get(checklist_item.id)
                        if workshop_qc_item and (
                                    item.get('is_applicable', True) != workshop_qc_item.is_applicable or
                                    (workshop_qc_item.has_issue == False and item.get('has_issue', False) == True)):
                            is_qc_failed = True

                    #bc_list.append(BookingChecklist(booking=booking, **item))
                    media_id_list = []
                    for m in media_list:
                        m['file'] = m.pop('image_name')
                        media = Media.objects.create(**m)
                        media_id_list.append(media.id)
                    bc_dict[checklist_item] = media_id_list
                    bc = BookingChecklist.objects.create(booking=booking, **item)
                    bc_objs.append(bc)
                #bc_objs = BookingChecklist.objects.filter(booking=booking, group_num=group_num)
                for bc_obj in bc_objs:
                    media_id_list = bc_dict.get(bc_obj.item, [])
                    for media_id in media_id_list:
                        through_list.append(ThroughModel(bookingchecklist_id=bc_obj.id, media_id=media_id))
                if through_list:
                    ThroughModel.objects.bulk_create(through_list)
                if is_qc_failed:
                    logger.exception("Checklist mismatch at time of driver ready to go for drop for id: %s",
                                     booking.id)
                    booking.ops_status_id = 47
                    booking.save()
        except Exception as e:
            logger.exception("Error in creating checklist")
            raise serializers.ValidationError("Error in creating checklist.")


def save_booking_change(booking, validated_data, old_booking):
    list_of_fields_to_update = ['workshop_eta', 'estimate_complete_time']
    delay_reason = validated_data.get('delay_reason')
    updated_by = validated_data.get('updated_by')
    reason_text = validated_data.get('reason_text')
    for key in list_of_fields_to_update:
        if validated_data.get(key):
            old_value = getattr(old_booking, key)
            new_value = getattr(booking, key)
            if old_value is not None:
                try:
                    if old_value != new_value:
                        change_type = EntityChangeTracker.CHANGE_TYPE_UPDATED
                    else:
                        change_type = EntityChangeTracker.CHANGE_TYPE_NOT_UPDATED
                        reason_text = "No Reason - Same ETA"
                    EntityChangeTracker.objects.create(content_type=EntityChangeTracker.CONTENT_TYPE_BOOKING,
                                                       content_id=booking.id, item_tracked=key,
                                                       change_type=change_type,
                                                       updated_by=updated_by, delay_reason=delay_reason,
                                                       reason_text=reason_text, old_value=old_value,
                                                       new_value=new_value)
                except:
                    logger.exception("Cannot create entry to track change in eta")


def update_booking(instance, validated_data):
    desc = validated_data.pop('desc', None)
    updated_by = validated_data.get('updated_by')
    device_type = validated_data.pop('device_type', None)
    action = validated_data.pop('action', None)
    workshop_images = validated_data.pop('workshop_images', [])
    # if action == constants.ACTION_PICKUP_SCHEDULED and validated_data.get('is_doorstep'):
    #     action = constants.ACTION_SCHEDULED
    status, ops_status = get_status_from_action(action)

    import copy
    booking_before_update = copy.deepcopy(instance)

    for attr, value in validated_data.items():
        if not isinstance(value, (list,dict)):
            setattr(instance, attr, value)

    if status and instance.status != status:
        instance.status = status
        instance.ops_status = ops_status
    if action and ops_status is not False:
        instance.ops_status = ops_status

    if desc:
        if instance.desc:
            instance.desc += "-------" + desc
        else:
            instance.desc = desc

    # If booking is assigned to Shonalee (group customerrelations) then notification will be sent.
    assigned_to_crm = False
    assigned_to = validated_data.get('assigned_to')
    if assigned_to and assigned_to.groups.filter(name='CustomerRelations').exists():
        assigned_to_crm = True

    updated_by_id = None
    if updated_by:
        updated_by_id = updated_by.id

    if action:
        # checking is action was taken and status has changed.
        #process_hooks.delay(instance.id, action)
        second_action = None
        if action == constants.ACTION_PICKUP_DRIVER_STARTED:
            instance.pickup_driver_start_time = timezone.now()

        elif action == constants.ACTION_TASK_TEAM_STARTED:
            instance.pickup_driver_start_time = timezone.now()

        elif action == constants.ACTION_DRIVER_AT_PICKUP_PLACE:
            instance.driver_arrived_pickup_time = timezone.now()

        elif action == constants.ACTION_TASK_TEAM_AT_TASK_LOCATION:
            instance.driver_arrived_pickup_time = timezone.now()

        elif action == constants.ACTION_CAR_PICKED_UP:
            instance.actual_pickup_time = timezone.now()

        elif action == constants.ACTION_CAR_REACHED_WORKSHOP:
            instance.workshop_reached_time = timezone.now()

        elif action == constants.ACTION_CAR_JOB_SCHEDULED:
            instance.estimate_work_start_time = timezone.now()

        elif action == constants.ACTION_WORK_IN_PROGRESS:
            instance.actual_work_start_time = timezone.now()

        elif action == constants.ACTION_WORK_COMPLETED:
            instance.actual_work_end_time = timezone.now()

        elif action == constants.ACTION_DROP_CAR_ON_THE_WAY:
            instance.drop_driver_start_time = timezone.now()
            invoice = BookingInvoice.objects.filter(booking=instance,
                                                    status=BookingInvoice.INVOICE_STATUS_PENDING).first()
            if invoice and not instance.return_wo_work:
                save_invoice(instance, update=True)

        elif action == constants.ACTION_CAR_REACHED_DROP_LOCATION:
            instance.driver_arrived_drop_time = timezone.now()
            invoice = BookingInvoice.objects.filter(booking=instance,
                                                    status=BookingInvoice.INVOICE_STATUS_PENDING).first()
            if invoice and not instance.return_wo_work:
                save_invoice(instance, update=True)

        elif action == constants.ACTION_CAR_DELIVERED:
            instance.actual_drop_time = timezone.now()

        elif action == constants.ACTION_RETURN_WO_WORK_DROP_SCHEDULE_PENDING:
            instance.return_wo_work = True

        elif action == constants.ACTION_BOOKING_CANCELLED:

            # +-----+----------------------------+----------------------------+--------+-------------+-----------------+--------------+------------+----------------+--------+-------------+--------+--------+------------+
            # | id | updated_at | created_at | status | payable_amt | amt_wo_discount | labour_price | part_price | material_price | vat | service_tax | kk_tax | sb_tax | booking_id |
            # +-----+----------------------------+----------------------------+--------+-------------+-----------------+--------------+------------+----------------+--------+-------------+--------+--------+------------+
            # | 413 | 2017 - 01 - 07 10:08:31.442858 | 2017 - 01 - 030 8:58:20.719251 | 2 | 2699.00 | 2699.00 | 1889.30 | 0.00 | 809.70 | 117.41 | 264.50 | 9.45 | 9.45 | 16675 |
            # | 422 | 2017 - 01 - 07 10:22:12.898835 | 2017 - 01 - 07 10:08:31.439411 | 2 | 2699.00 | 2699.00 | 1889.30 | 0.00 | 809.70 | 117.41 | 264.50 | 9.45 | 9.45 | 16675 |
            # | 423 | 2017 - 05 - 03 10:55:41.709951 | 2017 - 01 - 07 10:22:12.891515 | 1 | 2699.00 | 2699.00 | 1889.30 | 0.00 | 809.70 | 117.41 | 264.50 | 9.45 | 9.45 | 16675 |
            # +-----+----------------------------+----------------------------+--------+-------------+-----------------+--------------+------------+----------------+--------+-------------+--------+--------+------------+
            #  it is every time gives me the recently updated booking invoice so value is correct.
            # Ex: id = 423 for booking = 16675 and status is 1

            booking_invoice = BookingInvoice.objects.filter(booking=instance).first()  # Booking invoice
            if booking_invoice:
                invoice_status = booking_invoice.status
                # If there is invoice but it is not paid then cancel the invoice and then cancel booking
                if invoice_status != BookingInvoice.INVOICE_STATUS_PAID and invoice_status != BookingInvoice.INVOICE_STATUS_CANCELLED:
                    booking_invoice.status = BookingInvoice.INVOICE_STATUS_CANCELLED
                    booking_invoice.save()
                    logger.info('Invoice Exists, but it is not paid then cancel the invoice and then cancel booking')
                # if there is invoice but it is paid/partially paid then raise error.
                elif invoice_status == BookingInvoice.INVOICE_STATUS_PAID:
                    logger.info('Error : You cannot cancel the booking')
                    return False
            # if there is no invoice, then just cancel booking along with other things which happen already
            else:
                logger.info('no invoice, so booking is canceled')

            booking_proforma_invoice = BookingProformaInvoice.objects.filter(booking=instance).first()

            if booking_proforma_invoice:
                proforma_invoice_status = booking_proforma_invoice.status
                # If there is invoice but it is not paid then cancel the invoice and then cancel booking
                if proforma_invoice_status != BookingProformaInvoice.INVOICE_STATUS_PAID and proforma_invoice_status != BookingProformaInvoice.INVOICE_STATUS_CANCELLED:
                    booking_proforma_invoice.status = BookingProformaInvoice.INVOICE_STATUS_CANCELLED
                    booking_proforma_invoice.save()
                    logger.info('Proforma Invoice Exists, but it is not paid then cancel the invoice and then cancel booking')
                # if there is invoice but it is paid/partially paid then raise error.
                elif proforma_invoice_status == BookingProformaInvoice.INVOICE_STATUS_PAID:
                    logger.info('Error : You cannot cancel the booking')
                    return False
            # if there is no invoice, then just cancel booking along with other things which happen already
            else:
                logger.info('no invoice, so booking is canceled')
            BookingCoupon.objects.filter(booking=instance).delete()

        elif action == constants.ACTION_PENDING_PAYMENT or action == constants.ACTION_PENDING_PAYMENT_VAS:
            # If Pending payment is action, then do also Drop schedule pending for changes done for payment flow.
            # This is only being done to remove the "Pay Now" option and will be changed later when Pay Now option comes back again

            # create invoice
            invoice, bill_details, inv_message = save_invoice(instance)
            # invoice = BookingInvoice.objects.filter(booking=instance,
            #                                         status=BookingInvoice.INVOICE_STATUS_PENDING).first()
            p = Payment.objects.filter(invoice=invoice,tx_status=Payment.TX_STATUS_PENDING,
                                       tx_type=Payment.TX_TYPE_PAYMENT,
                                       payment_type=Payment.PAYMENT_TYPE_COD).first()
            if not p:
                p = Payment.objects.create(
                        invoice=invoice,
                        tx_status=Payment.TX_STATUS_PENDING,
                        payment_type=Payment.PAYMENT_TYPE_COD,
                        device_type=device_type
                    )

            instance.save()

            if action == constants.ACTION_PENDING_PAYMENT:
                second_action = constants.ACTION_DROP_SCHEDULE_PENDING
            else:
                second_action = constants.ACTION_CAR_REACHED_DROP_LOCATION
            status,ops_status = get_status_from_action(second_action)
            if status and instance.status != status:
                instance.status = status
                instance.ops_status = None
            if ops_status:
                instance.ops_status = ops_status

        instance.save()

        send_quick_pickup_notice = False
        if updated_by_id == instance.user.id and action in [constants.ACTION_PICKUP_SCHEDULED, constants.ACTION_SCHEDULED] \
                and ((timezone.localtime(timezone.now()).hour >= 18 and timezone.localtime(instance.pickup_time).date() == (
                            timezone.localtime(timezone.now()) + timezone.timedelta(days=1)).date())
                     or timezone.localtime(timezone.now()).hour <= 7 and timezone.localtime(instance.pickup_time).date() == timezone.localtime(timezone.now()).date()):
            logger.debug("Next day or same day booking scheduled.")
            from core.managers.generalManager import send_quick_pickup_notice_to_ops
            send_quick_pickup_notice_to_ops(instance.id)
            send_quick_pickup_notice = True

        if settings.PROCESS_IN_ASYNC:
            from core.tasks import process_hooks, handle_car_pickup_incentive_task, handle_car_pickup_referral_task, \
                update_event_respect_to_status_localytics
            process_hooks.delay(instance.id, action, sent_by_id=updated_by_id)

            if send_quick_pickup_notice:
                process_hooks.delay(instance.id, constants.ACTION_BOOKING_QUICK_PICKUP, sent_by_id=updated_by_id)

            if second_action:
                process_hooks.delay(instance.id, second_action, sent_by_id=updated_by_id)

            if action == constants.ACTION_CAR_PICKED_UP:
                handle_car_pickup_incentive_task.delay(instance.id)
                update_event_respect_to_status_localytics.delay("Car Picked up", instance.id)
                handle_car_pickup_referral_task.delay(instance.id)
            if action == constants.ACTION_CAR_DELIVERED:
                update_event_respect_to_status_localytics.delay("Car Delivered", instance.id)
        else:
            from core.managers.generalManager import process_hooks
            process_hooks(instance.id, action, sent_by_id=updated_by_id)
            from core.utils import update_event_to_localytics
            attrs = {'booking_id': str(instance.id), 'status_id': str(instance.status_id)}

            if send_quick_pickup_notice:
                process_hooks(instance.id, constants.ACTION_BOOKING_QUICK_PICKUP, sent_by_id=updated_by_id)

            if second_action:
                process_hooks(instance.id, second_action, sent_by_id=updated_by_id)

            if action == constants.ACTION_CAR_PICKED_UP:
                handle_car_pickup_incentive(instance)
                update_event_to_localytics(instance.user, "Car Picked up", attrs)
                handle_car_pickup_referral(instance)
            if action == constants.ACTION_CAR_DELIVERED:
                update_event_to_localytics(instance.user, "Car Delivered", attrs)

    else:
        instance.save()

    if settings.PROCESS_IN_ASYNC:
        from core.tasks import process_hooks
        if assigned_to_crm:
            process_hooks.delay(instance.id, constants.ACTION_BOOKING_BOOKING_ESCALATION, sent_by_id=updated_by_id)
        from core.tasks import update_booking_status_change_to_localytics
        update_booking_status_change_to_localytics.delay(instance.user_id, instance.status_id,
                                                         instance.status.status_desc)
    else:
        from core.managers.generalManager import process_hooks
        if assigned_to_crm:
            process_hooks(instance.id, constants.ACTION_BOOKING_BOOKING_ESCALATION, sent_by_id=updated_by_id)
        from core.utils import update_booking_change_to_localytics
        update_booking_change_to_localytics(instance.user, instance.status_id, instance.status.status_desc)

    for workshop_image in workshop_images:
        resource = Media.objects.create(
            file=workshop_image.get('image_name'),
            media_type=Media.MEDIA_TYPE_IMAGE,
            filename=workshop_image.get('actual_filename'),
            size=workshop_image.get('size'),
            content_type=workshop_image.get('content_type'),
            uploaded_to_s3=workshop_image.get('uploaded_to_s3')
        )
        BookingImage.objects.create(booking=instance, media=resource,
                                    panel_id=workshop_image.get('panel_id'),
                                    jobcard_type=workshop_image.get('jobcard_type'),
                                    status=instance.status, ops_status=instance.ops_status,
                                    image_type=workshop_image.get('image_type'),
                                    updated_by=updated_by,
                                    details=workshop_image.get('details'))

    booking_address = validated_data.get('booking_address')
    if booking_address:
        for booking_address_dict in booking_address:
            booking_address_dict['booking'] = instance
            ba = save_booking_address(booking_address_dict)

    #create_booking_ops_alerts(instance, validated_data, action)
    # create_qc_checks(instance, validated_data)
    create_checklist(instance, validated_data)

    save_booking_change(instance, validated_data, booking_before_update)

    return instance


def create_booking_image(validated_data):
    """
        create jobcard with media
    """
    uploaded_file = validated_data.get('media')
    uploaded_to_s3 = False
    image_name = validated_data.get('image_name')
    if uploaded_file:
        filename = uploaded_file.name
        size = uploaded_file.size
        content_type = uploaded_file.content_type
    elif image_name:
        filename=image_name
        uploaded_file = image_name
        size = validated_data.get('size')
        content_type = validated_data.get('content_type')
        uploaded_to_s3 = True
        if not content_type or not size:
            raise serializers.ValidationError("Missing size or content_type")
    else:
        raise serializers.ValidationError('Missing file!')

    booking = validated_data.get('booking')
    jobcard_type = validated_data.get('jobcard_type')
    image_type = validated_data.get('image_type', BookingImage.IMAGE_TYPE_JOBCARD)
    panel = validated_data.get('panel')
    updated_by = validated_data.get('updated_by')
    details = validated_data.get('details')
    # filename = uploaded_file.name
    # size = uploaded_file.size
    # content_type = uploaded_file.content_type

    resource = Media.objects.create(
        file=uploaded_file,
        media_type=Media.MEDIA_TYPE_IMAGE,
        filename=filename,
        size=size,
        content_type=content_type,
        uploaded_to_s3=uploaded_to_s3
    )

    # # TODO: remove old media from db and s3.
    # if booking_media:
    #     booking_media.media = resource
    #     booking_media.save()
    # else:
    booking_media = BookingImage.objects.create(booking=booking, media=resource, jobcard_type=jobcard_type,
                                                image_type=image_type, panel=panel, updated_by=updated_by,
                                                status=booking.status, ops_status=booking.ops_status,
                                                details=details)
    return booking_media


def get_media_url(request, media):
    if media.uploaded_to_s3:
        return build_s3_path(str(media.file),
                             bucket_name=settings.BOTO_S3_BUCKET_BOOKING)
    else:
        return build_local_path(str(media.file), request=request)


def filter_open_booking(queryset):
    return queryset.exclude(status_id__in=[22, 23, 24, 25])


def filter_closed_booking(queryset):
    return queryset.filter(status_id__in=[22, 23, 24, 25])


def get_booking_package_price(booking_package):
    return ((booking_package.part_price if booking_package.part_price is not None else decimal.Decimal('0.00')) +
            (booking_package.material_price if booking_package.material_price is not None else decimal.Decimal('0.00')) +
            (booking_package.labour_price if booking_package.labour_price is not None else decimal.Decimal('0.00')))


def get_booking_package_labour_price(booking_package):
    return booking_package.labour_price if booking_package.labour_price is not None else decimal.Decimal('0.00')


def get_booking_package_part_price(booking_package):
    return booking_package.part_price if booking_package.part_price is not None else decimal.Decimal('0.00')


def get_booking_package_material_price(booking_package):
    return booking_package.material_price if booking_package.material_price is not None else decimal.Decimal('0.00')


def get_booking_package_panel_price(booking_package_panel):
    return ((booking_package_panel.part_price if booking_package_panel.part_price is not None else decimal.Decimal('0.00')) +
            (booking_package_panel.material_price if booking_package_panel.material_price is not None else decimal.Decimal('0.00')) +
            (booking_package_panel.labour_price if booking_package_panel.labour_price is not None else decimal.Decimal('0.00')))


def get_booking_package_panel_labour_price(booking_package_panel):
    return booking_package_panel.labour_price if booking_package_panel.labour_price is not None else decimal.Decimal('0.00')


def get_booking_package_panel_part_price(booking_package_panel):
    return booking_package_panel.part_price if booking_package_panel.part_price is not None else decimal.Decimal('0.00')


def get_booking_package_panel_material_price(booking_package_panel):
    return booking_package_panel.material_price if booking_package_panel.material_price is not None else decimal.Decimal('0.00')


def get_editable_flag(booking_obj):
    booking_packages = booking_obj.booking_package.all()
    editable = False
    for bp in booking_packages:
        if bp.package.package.category == Package.CATEGORY_DENT:
            booking_package_panels = bp.booking_package_panel.all()
            for bpp in booking_package_panels:
                if bpp.panel.editable or bpp.panel.internal:
                    editable = True
                    break
        else:
            if bp.package.package.internal:
                editable = True
                break
    return editable


def get_booking_discount(booking_obj):
    # usually it will be only 1 but since it is a foreign key, it will return a list.
    booking_coupons = booking_obj.booking_coupon.all()
    discount_dict = {}

    #this will only be one but since it is a prefetch related, it will return a list. Will make it onetoone if required.
    booking_discounts = booking_obj.booking_discount.all()
    total_discount = decimal.Decimal('0.00')
    for bd in booking_discounts:
        total_discount += bd.labour_discount + bd.part_discount + bd.material_discount

    bumper_discount = total_discount

    booking_coupon_discount = decimal.Decimal('0.00')
    cashback_discount = decimal.Decimal('0.00')
    coupon_code = None
    coupon_id = None
    for bc in booking_coupons:
        total_discount += bc.discount
        booking_coupon_discount += bc.discount
        cashback_discount += bc.cashback
        coupon_id = bc.id
        coupon_code = bc.coupon.code

    if total_discount > decimal.Decimal('0.00') or coupon_code:
        discount_dict = {
            'coupon_discount': booking_coupon_discount,
            'cashback_discount': cashback_discount,
            'coupon_code': coupon_code,
            'coupon_id': coupon_id,
            'bumper_discount': bumper_discount
        }

    return discount_dict,total_discount


def get_bill_details_new(booking_obj):
    discount_dict,total_discount = get_booking_discount(booking_obj)
    return strip_decimals(get_bill_details_with_discount(booking_obj,discount_dict=discount_dict,
                                                         total_discount=total_discount))


def get_bill_details_with_discount(booking_obj,new_booking_invoice=None,discount_dict=None,total_discount=None):
    if not discount_dict:
        discount_dict = {}
    if not total_discount:
        total_discount = decimal.Decimal('0.0')
    booking_invoices = booking_obj.booking_invoice.all() # gives all booking invoices which are pending
    payments = []
    proforma_invoices = []
    booking_proforma_invoices = booking_obj.booking_proforma_invoice.all()
    advance_payment_received = decimal.Decimal('0.00')
    latest_booking_invoice = None
    pending_amt = decimal.Decimal('0.00')
    import itertools
    for booking_invoice in itertools.chain(booking_invoices, [new_booking_invoice]):
        if booking_invoice:
            if hasattr(booking_invoice, 'payments'):
                payments = payments + booking_invoice.payments
            if booking_invoice.status in [BookingInvoice.INVOICE_STATUS_PENDING, BookingInvoice.INVOICE_STATUS_PAID]:
                latest_booking_invoice = booking_invoice

    for booking_proforma_invoice in booking_proforma_invoices:
        if booking_proforma_invoice.status == BookingProformaInvoice.INVOICE_STATUS_PENDING:
            proforma_invoices.append(booking_proforma_invoice)
            pending_amt += booking_proforma_invoice.payable_amt
        if hasattr(booking_proforma_invoice, 'proforma_payments'):
            payments = payments + booking_proforma_invoice.proforma_payments
            for payment in booking_proforma_invoice.proforma_payments:
                if payment.tx_status == Payment.TX_STATUS_SUCCESS:
                    if payment.tx_type == Payment.TX_TYPE_PAYMENT:
                        advance_payment_received += payment.amount
                    else:
                        advance_payment_received -= payment.amount

    total_payment_received = decimal.Decimal('0.00')
    for payment in set(payments):
        if payment.tx_status == Payment.TX_STATUS_SUCCESS:
            if payment.tx_type == Payment.TX_TYPE_PAYMENT:
                total_payment_received += payment.amount
            else:
                total_payment_received -= payment.amount

    total_credits_used = decimal.Decimal('0.00')
    for credit in booking_obj.user.user_credittrx.all():
        if credit.entity_id == booking_obj.id and credit.trans_type == CreditTransaction.TRANSACTION_TYPE_DEBIT:
            total_credits_used += credit.amount

    invoice_id = None
    invoice_creation_date = None
    # Pay now - 1(Do not show button - invoice not created)
    # 2 (Show pay now button - invoice created but not paid)
    # 3 (Show PAID - invoice is paid)
    # TODO: fix all invoices where amount is paid but invoice is pending.
    pay_now = 1

    try:
        user_credit_obj = booking_obj.user.user_credit
        used_credits = user_credit_obj.credit
    except ObjectDoesNotExist:
        used_credits = decimal.Decimal('0.00')

    if new_booking_invoice or latest_booking_invoice:
        if not new_booking_invoice:
            new_booking_invoice = latest_booking_invoice
        payable_amt = max(decimal.Decimal('0.00'),
                          new_booking_invoice.payable_amt - total_payment_received - total_credits_used)
        if used_credits > payable_amt:
            used_credits = payable_amt
        payable_amt = max(decimal.Decimal('0.00'), payable_amt - used_credits)
        pending_amt = payable_amt
        amt_wo_discount = new_booking_invoice.amt_wo_discount
        total_sb_tax = new_booking_invoice.sb_tax
        total_kk_tax = new_booking_invoice.kk_tax
        total_service_tax = new_booking_invoice.service_tax
        total_vat = new_booking_invoice.vat
        total_cgst = new_booking_invoice.cgst
        total_sgst = new_booking_invoice.sgst
        total_igst = new_booking_invoice.igst
        total_gst = total_igst + total_sgst + total_cgst
        editable = get_editable_flag(booking_obj)
        invoice_id = new_booking_invoice.id
        invoice_creation_date = new_booking_invoice.created_at
        orig_payable_amt = new_booking_invoice.payable_amt
        if new_booking_invoice.status == BookingInvoice.INVOICE_STATUS_PENDING:
            pay_now = 2
        elif new_booking_invoice.status == BookingInvoice.INVOICE_STATUS_PAID:
            pay_now = 3
    else:
        amount_dict = get_bill_details_wo_invoice(booking_obj)
        amt_wo_discount = amount_dict.get('total_amt')
        total_service_tax = amount_dict.get('total_service_tax')
        total_kk_tax = amount_dict.get('total_kk_tax')
        total_sb_tax = amount_dict.get('total_sb_tax')
        total_vat = amount_dict.get('total_vat')
        total_cgst = amount_dict.get('total_cgst')
        total_sgst = amount_dict.get('total_sgst')
        total_igst = amount_dict.get('total_igst')
        total_gst = amount_dict.get('total_gst')
        editable = amount_dict.get('editable')
        payable_amt = max(0, amt_wo_discount + total_gst - total_discount - total_payment_received)
        orig_payable_amt = max(0, amt_wo_discount + total_gst - total_discount)

    from api.serializers.bookingSerializers import BookingProformaInvoiceSerializer
    return {
            "total_amt": amt_wo_discount,
            "total_service_tax": total_service_tax,
            "total_kk_tax": total_kk_tax,
            "total_sb_tax": total_sb_tax,
            "total_vat": total_vat,
            "total_cgst": total_cgst,
            "total_sgst": total_sgst,
            "total_igst": total_igst,
            "total_gst": total_gst,
            "total_discount": total_discount,
            "discount_dict": discount_dict,
            "editable": editable,
            "payable_amt": payable_amt,
            "invoice_id": invoice_id,
            "invoice_creation_date": invoice_creation_date,
            "proforma_invoices": BookingProformaInvoiceSerializer(booking_proforma_invoices,
                                                                  remove_fields=['booking'],
                                                                  many=True).data,
            "total_payment_received": total_payment_received,
            "advance_payment_received": advance_payment_received,
            "total_credits_used": total_credits_used,
            "orig_payable_amt": orig_payable_amt,
            "pay_now": pay_now,
            "pending_amt": pending_amt,
            "used_credits": used_credits
            }


def get_bill_details_old(booking_obj):
    discount_dict,total_discount = get_booking_discount(booking_obj)
    return get_bill_details_with_discount_old(booking_obj,discount_dict=discount_dict,total_discount=total_discount)


def get_bill_details_with_discount_old(booking_obj,booking_invoice=None,discount_dict=None,total_discount=None):
    if not discount_dict:
        discount_dict = {}
    if not total_discount:
        total_discount = decimal.Decimal('0.0')
    booking_invoices = booking_obj.booking_invoice.all() # gives all booking invoices which are pending
    if booking_invoice or booking_invoices:
        if not booking_invoice:
            booking_invoice = booking_invoices[0]
        payable_amt = booking_invoice.payable_amt
        amt_wo_discount = booking_invoice.amt_wo_discount
        editable = get_editable_flag(booking_obj)
    else:
        amount_dict = get_bill_details_wo_invoice(booking_obj)
        amt_wo_discount = amount_dict.get('total_amt')
        editable = amount_dict.get('editable')
        payable_amt = max(0, amt_wo_discount - total_discount)

    zero = decimal.Decimal('0.00')
    return { "total_amt": amt_wo_discount,
             "total_service_tax": zero,
             "total_kk_tax": zero,
             "total_sb_tax": zero,
             "total_vat": zero,
             "total_discount": int(total_discount),
             "discount_dict": discount_dict,
             "editable": editable,
             "payable_amt": payable_amt }


def save_invoice(booking, update=False, coupon_code=None, ignore_new=False):
    # get part_price, labour_price, material_price, get coupon details (discount amount) and discount from which one of these.
    # calculate coupon discount after removing discounts.
    logger.info("Inside save_invoice for booking: %s", booking.id)
    # get prices from packages and panels.
    amount_dict = get_bill_details_wo_invoice(booking)
    final_part_price = amount_dict.get('total_part_price')
    final_material_price = amount_dict.get('total_material_price')
    final_labour_price = amount_dict.get('total_labour_price')

    discount_dict = {}
    coupon = None
    message = None
    # get discount for coupon
    booking_coupon = None
    if coupon_code:
        # Coupon already used scenario to be handled.
        BookingCoupon.objects.filter(booking=booking).exclude(coupon__code=coupon_code).delete()
        discount_dict, message, coupon = get_coupon_details(booking, coupon_code)
        if coupon and discount_dict:
            booking_coupon = BookingCoupon.objects.create(coupon=coupon,booking=booking)
            discount_dict['coupon_id'] = booking_coupon.id
    if not (coupon and discount_dict):
        booking_coupon = BookingCoupon.objects.filter(booking=booking).first()
        if booking_coupon:
            coupon = booking_coupon.coupon
            discount_dict = get_coupon_discount(booking,coupon)

    # remove discount from part, material, labour prices
    total_discount = decimal.Decimal('0.0')
    if discount_dict:
        final_part_price = final_part_price - discount_dict.get('part_coupon_disc')
        final_material_price = final_material_price - discount_dict.get('material_coupon_disc')
        final_labour_price = final_labour_price - discount_dict.get('labour_coupon_disc')
        if booking_coupon:
            booking_coupon.discount = discount_dict.get('coupon_discount')
            booking_coupon.cashback = discount_dict.get('cashback_discount')
            booking_coupon.save()
            total_discount += booking_coupon.discount
        # TODO: scenario to handle a rare case that no discounted package or panel is there after the creation of invoice.

    # get discount by Bumper team. - We should do this only in exception cases.
    bumper_discounts = BookingDiscount.objects.filter(booking=booking)
    for bumper_discount in bumper_discounts:
        total_discount += bumper_discount.labour_discount + bumper_discount.material_discount + \
                          bumper_discount.part_discount
        final_labour_price -= bumper_discount.labour_discount
        final_material_price -= bumper_discount.material_discount
        final_part_price -= bumper_discount.part_discount

    payable_amt = final_part_price + final_material_price + final_labour_price

    # service_tax_factor = constants.SERVICE_TAX_FACTOR
    # kk_tax_factor = constants.KK_TAX_FACTOR
    # sb_tax_factor = constants.SB_TAX_FACTOR
    # vat_factor = constants.VAT_FACTOR
    # city = booking.city
    # if city:
    #     service_tax_factor = city.service_tax
    #     kk_tax_factor = city.kk_tax
    #     sb_tax_factor = city.sb_tax
    #     vat_factor = city.vat
    #
    # taxable_amt = ((decimal.Decimal('10000.00') * payable_amt)/
    #                (decimal.Decimal('10000.00') +
    #                 decimal.Decimal('70.00') * (service_tax_factor+sb_tax_factor+kk_tax_factor) +
    #                 decimal.Decimal('75.00') * vat_factor))
    # # calculate taxes on the discounted payable amount
    # # 70% of payable amt (without tax) will be considered for service tax, kk_tax and sb_tax.
    # # payable amt is price including tax. So reverse calculation for calulation of taxes.
    # service_tax = (taxable_amt * decimal.Decimal('70.00') * service_tax_factor / decimal.Decimal('10000.00')
    #                ).quantize(constants.TWO_PLACES)
    # kk_tax = (taxable_amt * decimal.Decimal('70.00') * kk_tax_factor / decimal.Decimal('10000.00')
    #           ).quantize(constants.TWO_PLACES)
    # sb_tax = (taxable_amt * decimal.Decimal('70.00') * sb_tax_factor / decimal.Decimal('10000.00')
    #           ).quantize(constants.TWO_PLACES)
    #
    # # 75 % of payable amt (without tax) will be considered for vat.
    # vat = (taxable_amt * decimal.Decimal('75.00') * vat_factor / decimal.Decimal('10000.00')
    #        ).quantize(constants.TWO_PLACES)
    #
    # # vat += ((final_part_price * vat_factor) /
    # #         (decimal.Decimal('100.00') + vat_factor)
    # #         ).quantize(constants.TWO_PLACES)
    #
    # # old calculation
    # # service_tax = (constants.SERVICE_TAX_FACTOR * final_labour_price).quantize(constants.TWO_PLACES)
    # # kk_tax = (constants.KK_TAX_FACTOR * final_labour_price).quantize(constants.TWO_PLACES)
    # # sb_tax = (constants.SB_TAX_FACTOR * final_labour_price).quantize(constants.TWO_PLACES)
    # # vat = (constants.VAT_FACTOR * (final_part_price + final_material_price)).quantize(constants.TWO_PLACES)

    service_tax = kk_tax = sb_tax = vat = decimal.Decimal('0.00')
    cgst_factor = constants.CGST_FACTOR
    sgst_factor = constants.SGST_FACTOR
    igst_factor = constants.IGST_FACTOR
    city = booking.city
    if city:
        cgst_factor = city.cgst
        sgst_factor = city.sgst
        igst_factor = city.igst

    # If pickup address is of Delhi, then igst will be applicable.
    ba = BookingAddress.objects.filter(booking=booking,
                                       type=BookingAddress.ADDRESS_TYPE_PICKUP).select_related('address').first()
    if ba and ba.address.state in ['Delhi', 'DL']:
        cgst_factor = decimal.Decimal('0.00')
        sgst_factor = decimal.Decimal('0.00')
    else:
        igst_factor = decimal.Decimal('0.00')

    for_old_invoice = False
    if booking.created_at.date() < datetime.strptime('25082017', "%d%m%Y").date():
        for_old_invoice = True
    if for_old_invoice:
        taxable_amt = ((decimal.Decimal('100.00') * payable_amt) / (decimal.Decimal('100.00') +
                        cgst_factor + sgst_factor + igst_factor))
    else:
        taxable_amt = payable_amt

    # payable amt is price including tax. So reverse calculation for calulation of taxes.
    cgst = (taxable_amt * cgst_factor / decimal.Decimal('100.00')).quantize(constants.TWO_PLACES)
    sgst = (taxable_amt * sgst_factor / decimal.Decimal('100.00')).quantize(constants.TWO_PLACES)
    igst = (taxable_amt * igst_factor / decimal.Decimal('100.00')).quantize(constants.TWO_PLACES)

    if not for_old_invoice:
        # Payable amount now includes taxes
        payable_amt = payable_amt + cgst + sgst + igst

    existing_invoices = booking.booking_invoice.all().exclude(status=BookingInvoice.INVOICE_STATUS_CANCELLED)

    # proforma_invoices = BookingProformaInvoice.objects.filter(booking=booking).exclude(
    #                                         status=BookingProformaInvoice.INVOICE_STATUS_CANCELLED)

    success_payments = Payment.objects.filter(Q(invoice__booking=booking) |
                                              Q(proforma_invoice__booking=booking),
                                              tx_status=Payment.TX_STATUS_SUCCESS)

    new_invoice = None
    if existing_invoices and update:
        for invoice in existing_invoices:
            if invoice.status == BookingInvoice.INVOICE_STATUS_PENDING or ignore_new:
                invoice.amt_wo_discount = amount_dict.get('total_amt')
                invoice.payable_amt = payable_amt
                invoice.service_tax = service_tax
                invoice.sb_tax = sb_tax
                invoice.kk_tax = kk_tax
                invoice.vat = vat
                invoice.cgst = cgst
                invoice.sgst = sgst
                invoice.igst = igst
                invoice.labour_price = final_labour_price
                invoice.material_price = final_material_price
                invoice.part_price = final_part_price
                invoice.save()
                new_invoice = invoice

    if not new_invoice:
        new_invoice = BookingInvoice.objects.create(booking=booking,
                                                    status=BookingInvoice.INVOICE_STATUS_PENDING,
                                                    amt_wo_discount=amount_dict.get('total_amt'),
                                                    labour_price=final_labour_price,
                                                    material_price=final_material_price,
                                                    part_price=final_part_price,
                                                    payable_amt=payable_amt,
                                                    service_tax=service_tax, kk_tax=kk_tax,
                                                    sb_tax=sb_tax, vat=vat, cgst=cgst, sgst=sgst, igst=igst)

        for invoice in existing_invoices:
            invoice.status = BookingInvoice.INVOICE_STATUS_CANCELLED
            invoice.save()

    total_amt_paid = decimal.Decimal('0.00')
    for payment in success_payments:
        total_amt_paid += payment.amount
        if payment.invoice_id != new_invoice.id:
            payment.invoice = new_invoice
            payment.save()

    if total_amt_paid >= new_invoice.payable_amt:
        new_invoice.status = BookingInvoice.INVOICE_STATUS_PAID
        new_invoice.save()

    return new_invoice, get_bill_details_with_discount(booking, new_booking_invoice=new_invoice,
                                                       discount_dict=discount_dict,
                                                       total_discount=total_discount), message


def update_followup(instance, validated_data):
    followup = validated_data.pop('followup',[])
    updated_by = validated_data.pop('updated_by')

    from core.tasks import send_custom_notification_task

    for f in followup:
        f['updated_by'] = updated_by
        tags = f.pop('tags',[])
        followup_obj = instance.followup.create(**f)
        if tags:
            followup_obj.tags.add(*tags)
        result = f.get('result')
        if result and result.notification:
            notification = result.notification
            send_custom_notification_task.delay(notification.name,
                                                {'instance_id': instance.id,
                                                 'result_name': result.name,
                                                 'followup_for_type': 'Booking'
                                                 })

    is_instance_changed = False
    for attr, value in validated_data.items():
        if not isinstance(value, (list,dict)):
            is_instance_changed = True
            setattr(instance, attr, value)

    if is_instance_changed:
        instance.updated_by = updated_by
        instance.save()

    return instance


def get_action_from_booking(booking):
    found_action = None
    for key, value in constants.ACTION_DICT.items():
        if value.get('status') == booking.status_id and value.get('ops_status') == booking.ops_status_id:
            found_action = key
            break
    return found_action


def get_rework_details(booking):
    from api.serializers.bookingSerializers import BookingReworkPackagePanelSerializer, BookingReworkPackageSerializer
    rework_package_queryset = BookingReworkPackage.objects.filter(booking_package__booking=booking)
    rework_package_queryset = rework_package_queryset.select_related(
                                                          'booking_package',
                                                          'booking_package__package',
                                                          'booking_package__package__package'
                                                          )
    rework_panel_queryset = BookingReworkPackagePanel.objects.filter(
                                                    booking_package_panel__booking_package__booking=booking)
    rework_panel_queryset = rework_panel_queryset.select_related(
                                                        'booking_package_panel__panel',
                                                        'booking_package_panel__panel__car_panel'
                                                        )

    return {
        'rework_packages': BookingReworkPackageSerializer(
                    rework_package_queryset,
                    many=True).data,
        'rework_panels': BookingReworkPackagePanelSerializer(
                    rework_panel_queryset,
                    many=True).data
    }


def get_latest_eod_message(booking):
    latest_message = booking.message_booking.first()
    if latest_message:
        return {'message': latest_message.message,
                'created_at': latest_message.created_at,
                'updated_at': latest_message.updated_at
                }
    return None


def can_close_booking(booking):
    message = None
    # delivery, drop, pick up date & reg number, workshop name & driver name, workshop & customer eta package exists
    booking_package = BookingPackage.objects.filter(booking=booking).first()  # Booking package
    booking_invoice = BookingInvoice.objects.filter(booking=booking).first()  # Booking invoice
    if not booking.return_wo_work:
        if not booking.actual_pickup_time:
            message = "actual pickup time is missing update it and then close booking"
            return message,False
        elif not booking.actual_drop_time:
            message = "actual drop time is missing update it and then close booking"
            return message,False
        elif not booking.workshop_eta:
            message = "workshop eta is missing update it and then close booking"
            return message,False
        elif not booking.usercar.registration_number:
            message = "user car registration number is missing update it and then close booking"
            return message,False
        elif not booking.estimate_complete_time:
            message = "customer eta is missing update it and then close booking"
            return message,False
        elif not booking.workshop_id:
            message = "workshop id is missing update it and then close booking"
            return message,False
        elif not booking.pickup_driver_id:
            message = "pickup driver name is missing update it and then close booking"
            return message,False
        elif not booking.drop_driver_id:
            message = "drop driver name is missing update it and then close booking"
            return message,False
        elif not booking_package:
            message = "no package in the booking update it and then close booking"
            return message,False
        elif not booking_invoice:
            message = "Booking invoice is missing in the booking update it and then close booking"
            return message,False
        elif booking_invoice.status != BookingInvoice.INVOICE_STATUS_PAID:
            message = "Paid invoice is missing in the booking update it and then close booking"
            return message, False

        # Booking image - Documents (Handover, Inspection Sheet, JobCard)
        booking_image = BookingImage.objects.filter(booking=booking).values('image_type').\
            annotate(total=Count('image_type'))
        image_types = BookingImage.IMAGE_TYPES
        # Set(image_type) - Set(booking_image's (image_type) will give the missing docs
        image_not_present = set([(d[0]) for d in image_types])-set([(d['image_type']) for d in booking_image])
        image_type_dictionary = dict(image_types)
        # Checking if the set - image_not_present is empty or not. if not empty continue pop elements out
        if image_not_present:
            missing_doc_name = None
            while image_not_present:
                missing_doc_name = image_type_dictionary[image_not_present.pop()]
                logger.info('missing_docs_name: %s', missing_doc_name)
            message = missing_doc_name + ' is missing in the booking. update it and then close booking'
            return message, False
        else:
            logger.info('image_not_preset set is empty. so All Docs Present inside the booking')
    else:
        if not booking.actual_pickup_time:
            message = "actual pickup time is missing update it and then close booking"
            return message,False
        elif not booking.actual_drop_time:
            message = "actual drop time is missing update it and then close booking"
            return message,False
        elif not booking.workshop_eta:
            message = "workshop eta is missing update it and then close booking"
            return message,False
        elif not booking.usercar.registration_number:
            message = "user car registration number is missing update it and then close booking"
            return message,False
        elif not booking.pickup_driver_id:
            message = "pickup driver name is missing update it and then close booking"
            return message,False
        elif not booking.drop_driver_id:
            message = "drop driver name is missing update it and then close booking"
            return message,False
        elif not booking_package:
            message = "no package in the booking update it and then close booking"
            return message,False
    return message, True


def get_call_screen_dict(booking=None, user=None):
    """
    :param booking: Optional
    :param user: Optional
    :return:
    """
    from api.serializers.userSerializer import UserSerializer
    current_time = timezone.localtime(timezone.now())
    current_date = current_time.date()

    booking_help = {
        "enable": False,
        "popup_message": None,
        "call_details": None
    }
    pickup_help = booking_help.copy()
    workshop_help = booking_help.copy()
    drop_help = booking_help.copy()
    escalation_and_feedback = booking_help.copy()
    general_inquiry = booking_help.copy()

    if booking:
        if 1 <= booking.status.flow_order_num <= 3 and (
                not booking.pickup_time or (booking.pickup_time and (
                            booking.pickup_time.date() > current_date or booking.ops_status_id not in (3,4)))):
            booking_help["enable"] = True
            if 9 <= current_time.hour <= 17 and current_time.weekday() != 6:
                booking_help["popup_message"] = "Call customer care executive"
                if booking.caller:
                    booking_help["call_details"] = UserSerializer(booking.caller,
                                                                  new_fields=["name", "ops_phone", "email"]).data
                else:
                    booking_help["call_details"] = {"name": None, "ops_phone": "9108446586", "email": None}
            else:
                booking_help["popup_message"] = "Available between 9:00 AM and 6:00 PM from Monday to Saturday"
        if 4 <= booking.status.flow_order_num <= 10 or (
                            booking.pickup_time and booking.pickup_time.date() == current_date and
                            booking.status_id == 3 and booking.ops_status_id in (3,4)):
            pickup_help["enable"] = True
            pickup_help["popup_message"] = "Call crew member"
            if booking.pickup_driver:
                pickup_help["call_details"] = UserSerializer(booking.pickup_driver,
                                                             new_fields=["name", "ops_phone", "email"]).data
            else:
                pickup_help["call_details"] = {"name": None, "ops_phone": "9108446586", "email": None}
        if 10 <= booking.status.flow_order_num <= 19:
            workshop_help["enable"] = True
            drop_time = booking.drop_time
            if not drop_time:
                drop_time = booking.estimate_complete_time
            if (9 <= current_time.hour <= 17 and current_time.weekday() != 6) or (
                        drop_time and drop_time.date() == current_date):
                workshop_help["popup_message"] = "Call workshop associate"
                if booking.workshop_asst_mgr:
                    workshop_help["call_details"] = UserSerializer(booking.workshop_asst_mgr,
                                                                   new_fields=["name", "ops_phone", "email"]).data
                else:
                    workshop_help["call_details"] = {"name": None, "ops_phone": "9108446586", "email": None}
            else:
                workshop_help["popup_message"] = "Available between 9:00 AM and 6:00 PM from Monday to Saturday"
        if 20 <= booking.status.flow_order_num <= 22:
            drop_help["enable"] = True
            drop_help["popup_message"] = "Call crew member"
            if booking.drop_driver:
                drop_help["call_details"] = UserSerializer(booking.drop_driver,
                                                           new_fields=["name", "ops_phone", "email"]).data
            else:
                drop_help["call_details"] = {"name": None, "ops_phone": "9108446586", "email": None}
    else:
        booking_help["enable"] = True
        if user:
            booking_help["popup_message"] = "No active booking"
        else:
            booking_help["popup_message"] = "Please login to reach out to right person"

    escalation_and_feedback["enable"] = True
    if 9 <= current_time.hour <= 17 and current_time.weekday() != 6:
        escalation_and_feedback["popup_message"] = "Call customer experience executive"
        escalation_and_feedback["call_details"] = {"name": None, "ops_phone": "9686207009", "email": None}
    else:
        escalation_and_feedback["popup_message"] = "Available between 9:00 AM and 6:00 PM from Monday to Saturday"

    general_inquiry["enable"] = True
    if 9 <= current_time.hour <= 17 and current_time.weekday() != 6:
        general_inquiry["popup_message"] = "Call helpline"
        general_inquiry["call_details"] = {"name": None, "ops_phone": "9108446586", "email": None}
    else:
        general_inquiry["popup_message"] = "Available between 9:00 AM and 6:00 PM from Monday to Saturday"

    return {
        "booking_help": booking_help,
        "pickup_help": pickup_help,
        "drop_help": drop_help,
        "workshop_help": workshop_help,
        "escalation_and_feedback": escalation_and_feedback,
        "general_inquiry": general_inquiry,
    }
