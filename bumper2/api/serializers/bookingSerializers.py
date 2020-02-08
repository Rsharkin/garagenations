from django.db.models import Prefetch
from rest_framework import serializers

from core.models import EntityChangeTracker
from core.models.booking import (
    Booking,
    BookingPackage,
    BookingPackagePanel,
    BookingAddress,
    BookingCheckpoint,
    BookingImage,
    BookingDiscount,
    BookingCoupon,
    BookingFeedback,
    BookingCustFeedback,
    BookingProformaInvoice,
    BookingInvoice,
    BookingReworkPackage,
    BookingReworkPackagePanel,
    BookingQualityChecks,
    TeamAlert,
    BookingHandoverItem,
    BookingChecklist,
    BookingFlag,
    BookingPartDoc,
    BookingPartQuote,
    PartDocNote,
    PartQuoteNote,
    BookingExpectedEOD
)
from core.constants import ACTION_DICT
from core.models.users import Followup, CreditTransaction
from core.models.payment import Payment
from core.models.message import Messages
from core.models.master import PackagePrice, BookingStatus, City, Package, BookingOpsStatus, CarPanelPrice, \
    CarReturnReasons, FlagType, PartDocStatus, PartVendor
from masterSerializers import (
    PackagePriceSerializer,
    CarPanelPriceSerializer,
    WorkshopSerializer,
    PackageSerializer,
    CarPanelSerializer,
    QualityCheckSerializer,
    TeamAlertReasonSerializer,
    HandoverItemSerializer,
    DelayReasonsSerializer,
    ChecklistItemSerializer,
    ReturnReasonsSerializer,
    DiscountReasonsSerializer,
    FlagTypeSerializer,
    GenericModelSerializer
)
from commonSerializers import AddressSerializer, DynamicFieldsModelSerializer, MediaSerializer
from core.managers import bookingManager,paymentManager
from userSerializer import UserSerializer, UserCarSerializer, FollowupSerializer
from commonSerializers import ConflictAwareModelSerializer
from custom_serializer_fields import CreateListModelMixin, ObjectUserValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.conf import settings
from core.tasks import send_custom_notification_task
from django.utils import timezone

import logging
logger = logging.getLogger(__name__)


class TestedQualityCheckSerializer(serializers.ModelSerializer):
    # quality_check_id = serializers.IntegerField(required=True)
    # is_passed = serializers.BooleanField(required=True)
    # failure_reason = serializers.CharField(max_length=1024, required=False)
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                    queryset=get_user_model().objects.all())
    class Meta:
        model = BookingQualityChecks
        exclude = ('booking', 'booking_image')


class BookingHandoverItemCreateSerializer(serializers.ModelSerializer):
    # group = serializers.IntegerField(
    #     read_only=True,
    #     default=serializers.CreateOnlyDefault(bookingManager.get_handover_group)
    # )
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                    queryset=get_user_model().objects.all())
    class Meta:
        model = BookingHandoverItem
        exclude = ('booking',)
        extra_kwargs = {'status': {'required': False},'ops_status': {'required': False}}


class BookingChecklistItemCreateSerializer(serializers.ModelSerializer):
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                    queryset=get_user_model().objects.all())
    media = serializers.ListField(child=MediaSerializer(remove_fields=['media_type', 'desc']), required=False)

    class Meta:
        model = BookingChecklist
        exclude = ('booking',)
        extra_kwargs = {'status': {'required': False},'ops_status': {'required': False}}


class BookingPackagePanelSerializer(ConflictAwareModelSerializer):
    panel_details = CarPanelPriceSerializer(source='panel', remove_fields=['city'], read_only=True)
    price = serializers.SerializerMethodField()
    price_text = serializers.SerializerMethodField()
    # rework_panel = BookingReworkPackagePanelSerializer(many=True, read_only=True,
    #                                                    remove_fields=['booking_package_panel',
    #                                                                   'panel_details'])

    class Meta:
        model = BookingPackagePanel
        fields = ('id','booking_package','panel_details','panel','price',
                  'part_price','material_price','labour_price','rework','price_text', 'extra')

    def get_price(self,obj):
        price = bookingManager.get_booking_package_panel_price(obj)
        return str(price)

    def get_price_text(self, obj):
        price = bookingManager.get_booking_package_panel_price(obj)
        if obj.panel.type_of_work in [CarPanelPrice.TYPE_OF_WORK_REPLACE, CarPanelPrice.TYPE_OF_WORK_REPLACE_FBB]:
            if obj.part_price is None and obj.material_price is None and obj.labour_price is None:
                return "Part MRP*"
            elif obj.part_price is None:
                return "&#8377; " + str(int(price)) + " + Part MRP*"
        return "&#8377; " + str(price)

    def create(self, validated_data):
        booking_package = validated_data.get('booking_package')
        if booking_package.booking.status.flow_order_num >= 15:
            raise serializers.ValidationError("Cannot add panel after Work Completed.")
        if booking_package.booking.rework_booking_id is not None:
            panel = validated_data.get('panel')
            extra = validated_data.get('extra')
            if panel and not extra:
                validated_data['part_price'] = 0
                validated_data['material_price'] = 0
                validated_data['labour_price'] = 0
        return super(BookingPackagePanelSerializer,self).create(validated_data)

    def update(self, instance, validated_data):
        booking = instance.booking_package.booking
        if booking.status.flow_order_num >= 15:
            raise serializers.ValidationError("Cannot update package after Work Completed.")

        if validated_data.get('part_price') or validated_data.get('material_price') or \
                validated_data.get('labour_price'):
            if not instance.panel.editable:
                raise serializers.ValidationError("Price not editable for for this panel/part.")

        extra = validated_data.get('extra')
        if not extra:
            extra = instance.extra
        if booking.rework_booking_id is not None and not extra:
            validated_data['part_price'] = 0
            validated_data['material_price'] = 0
            validated_data['labour_price'] = 0
        else:
            if validated_data.get('part_price') or validated_data.get('material_price') or \
                    validated_data.get('labour_price'):
                pass
            else:
                instance.part_price = None
                instance.material_price = None
                instance.labour_price = None

        return super(BookingPackagePanelSerializer,self).update(instance, validated_data)


class BookingPackageSerializer(ConflictAwareModelSerializer):
    package = PackagePriceSerializer(remove_fields=['city'], read_only=True)
    package_id = serializers.PrimaryKeyRelatedField(queryset=PackagePrice.objects.all(),
                                                    source='package', write_only=True)
    booking_package_panel = BookingPackagePanelSerializer(remove_fields=['booking_package'],
                                                          many=True, required=False)
    manual_price = serializers.DecimalField(max_digits=10,decimal_places=2,write_only=True,required=False)
    price = serializers.SerializerMethodField()
    #service_tax = serializers.SerializerMethodField()
    #vat = serializers.SerializerMethodField()
    # rework_package = BookingReworkPackageSerializer(many=True, read_only=True,
    #                                                 remove_fields=['booking_package',
    #                                                                'booking_package_details'])

    class Meta:
        model = BookingPackage
        fields = ('id','package','booking','package_id','booking_package_panel',
                  'price','manual_price',
                  'part_price','material_price','labour_price',
                  'rework', 'extra'
                  )

    def get_price(self,obj):
        price = Decimal('0.00')
        if obj.package.package.category == Package.CATEGORY_DENT:
            for panel in obj.booking_package_panel.all():
                price += bookingManager.get_booking_package_panel_price(panel)
        else:
            price = bookingManager.get_booking_package_price(obj)
        return str(price)

    # def get_service_tax(self,obj):
    #     service_tax = Decimal('0.00')
    #     if obj.package.package.category == Package.CATEGORY_DENT:
    #         for panel in obj.booking_package_panel.all():
    #             service_tax += bookingManager.get_booking_package_panel_service_tax(panel)
    #     else:
    #         service_tax = obj.service_tax
    #     return str(service_tax)

    # def get_vat(self,obj):
    #     vat = Decimal('0.00')
    #     if obj.package.package.category == Package.CATEGORY_DENT:
    #         for panel in obj.booking_package_panel.all():
    #             vat += bookingManager.get_booking_package_panel_vat(panel)
    #     else:
    #         vat = obj.vat
    #     return str(vat)

    def create(self, validated_data):
        booking = validated_data.get('booking')
        if booking.status.flow_order_num >= 15:
            raise serializers.ValidationError("Cannot add package after Work Completed.")
        bp_panels = validated_data.pop('booking_package_panel',[])
        validated_data['price'] = validated_data.pop('manual_price',None)

        extra = validated_data.get('extra')
        if booking.rework_booking_id is not None and not extra:
            validated_data['part_price'] = 0
            validated_data['material_price'] = 0
            validated_data['labour_price'] = 0

        bp_obj = BookingPackage.objects.create(**validated_data)
        if bp_obj.package.package.category == Package.CATEGORY_DENT:
            for bp_panel in bp_panels:
                extra = bp_panel.get('extra')
                if booking.rework_booking_id is not None and not extra:
                    bp_panel['part_price'] = 0
                    bp_panel['material_price'] = 0
                    bp_panel['labour_price'] = 0
                BookingPackagePanel.objects.create(booking_package=bp_obj, **bp_panel)
        return bp_obj

    def update(self, instance, validated_data):
        booking = instance.booking
        if booking.status.flow_order_num >= 15:
            raise serializers.ValidationError("Cannot update package after Work Completed.")
        bp_panels = validated_data.pop('booking_package_panel',[])

        extra = validated_data.get('extra')
        if booking.rework_booking_id is not None and not extra:
            validated_data['part_price'] = 0
            validated_data['material_price'] = 0
            validated_data['labour_price'] = 0

        for attr, value in validated_data.items():
            if not isinstance(value, (list,dict)):
                setattr(instance, attr, value)

        if instance.package.package.category == Package.CATEGORY_DENT:
            if bp_panels:
                BookingPackagePanel.objects.filter(booking_package=instance).delete()
                for bp_panel in bp_panels:
                    extra = bp_panel.get('extra')
                    if booking.rework_booking_id is not None and not extra:
                        bp_panel['part_price'] = 0
                        bp_panel['material_price'] = 0
                        bp_panel['labour_price'] = 0
                    BookingPackagePanel.objects.create(booking_package=instance,**bp_panel)

        return instance


class BookingAddressSerializer(DynamicFieldsModelSerializer):
    address = AddressSerializer(remove_fields=['id'],read_only=True)
    useraddress_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BookingAddress
        fields = ('__all__')
        read_only_fields=('user',)

    def create(self, validated_data):
        ba = bookingManager.save_booking_address(validated_data)
        return ba


class BookingCheckpointSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = BookingCheckpoint
        fields = ('__all__')
        depth = 1


class BookingFlagSerializer(serializers.ModelSerializer):
    flag_type = FlagTypeSerializer(read_only=True)

    class Meta:
        model = BookingFlag
        fields = '__all__'

    def to_internal_value(self, data):
        self.fields['flag_type'] = serializers.PrimaryKeyRelatedField(queryset=FlagType.objects.filter(active=True),
                                                                      required=False)
        return super(BookingFlagSerializer, self).to_internal_value(data)

    def to_representation(self, obj):
        if self.fields.get('flag_type'):
            self.fields['flag_type'] = FlagTypeSerializer()
        return super(BookingFlagSerializer, self).to_representation(obj)


class BookingBillSerializer(DynamicFieldsModelSerializer):
    booking_package = BookingPackageSerializer(many=True, remove_fields=['booking'])
    bill_details = serializers.SerializerMethodField()
    payment_details = serializers.SerializerMethodField()
    user = UserSerializer(remove_fields=['city','designation','company_name',
                                         'city_id','groups','ops_phone','user_credit',
                                         'is_email_verified', 'active_devices',
                                         'user_detail','referral'])
    class Meta:
        model = Booking
        fields = ('booking_package','bill_details','id','payment_details','user')

    def get_bill_details(self, obj):
        return bookingManager.get_bill_details_old(obj)

    def get_payment_details(self, obj):
        return paymentManager.get_payment_details(obj)

    @classmethod
    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('status',
                                           'ops_status',
                                           'user').prefetch_related('booking_package',
                                                                    'booking_package__booking_package_panel',
                                                                    'booking_package__booking_package_panel__panel',
                                                                    'booking_package__booking_package_panel__panel__car_panel',
                                                                    'booking_package__package',
                                                                    'booking_package__package__package',
                                                                    'booking_discount',
                                                                    'booking_invoice',
                                                                     Prefetch(
                                                                       "booking_invoice__invoice_payment",
                                                                        queryset=Payment.objects.filter(payment_for=Payment.PAYMENT_FOR_USER,
                                                                                                        tx_type=Payment.TX_TYPE_PAYMENT).order_by('-id'),
                                                                        to_attr='payments'
                                                                        ),
                                                                     'user__user_credit',
                                                                     'booking_coupon',
                                                                     'booking_coupon__coupon'
                                                                     )
        return queryset


class BookingStatusSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = BookingStatus
        fields = ('__all__')


class BookingOpsStatusSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = BookingOpsStatus
        fields = ('__all__')


class PaymentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Payment
        fields = ('__all__')


class BookingSerializer(serializers.ModelSerializer):
    # booking_package = BookingPackageSerializer(many=True, remove_fields=['booking'],required=False)
    booking_package = BookingPackageSerializer(many=True, remove_fields=['booking'],
                                               change_serializer={
                                                   'booking_package_panel':BookingPackagePanelSerializer(
                                                       remove_fields=['booking_package'],
                                                       many=True,
                                                       required=False)},
                                               required=False)
    booking_address = BookingAddressSerializer(many=True, remove_fields=['booking'], required=False)
    bill_details = serializers.SerializerMethodField()
    payment_details = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    status = BookingStatusSerializer(read_only=True)
    ops_status = BookingOpsStatusSerializer(read_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False)
    action = serializers.IntegerField(write_only=True,required=False)
    booking_checkpoint = BookingCheckpointSerializer(many=True, remove_fields=['booking'],read_only=True)
    #quoted_price = serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)
    pickup_driver_details = UserSerializer(read_only=True, source='pickup_driver',
                                           remove_fields=['groups','user_credit','city','active_devices','user_detail',
                                                          'referral'])
    drop_driver_details = UserSerializer(read_only=True, source='drop_driver',
                                         remove_fields=['groups','user_credit','city','active_devices','user_detail',
                                                        'referral'])
    workshop_manager_details = UserSerializer(read_only=True, source='workshop_manager',
                                              remove_fields=['groups','user_credit','city','active_devices',
                                                             'user_detail','referral'])
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), source='user', write_only=True, required=False)
    #payments = serializers.SerializerMethodField()
    booking_rework = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    workshop_images = serializers.ListField(write_only=True, required=False, child=serializers.DictField())
    eod_message = serializers.SerializerMethodField()
    checked_items = serializers.ListField(child=TestedQualityCheckSerializer(), write_only=True, required=False)
    item_list = serializers.ListField(child=BookingChecklistItemCreateSerializer(),
                                      write_only=True, required=False)
    reason_text = serializers.CharField(write_only=True, required=False, allow_null=True) # Reason for delay.
    return_reason = ReturnReasonsSerializer()
    booking_flag = BookingFlagSerializer(read_only=True, many=True)

    class Meta:
        model = Booking
        exclude = ('followup',)
        #fields = ('booking_package','booking_address','status','booking_bill','user','city','booking_checkpoint','action')

    def to_internal_value(self, data):
        self.fields['return_reason'] = serializers.PrimaryKeyRelatedField(queryset=CarReturnReasons.objects.all(),
                                                                          required=False)
        return super(BookingSerializer, self).to_internal_value(data)

    def to_representation(self, obj):
        self.fields['return_reason'] = ReturnReasonsSerializer()
        self.fields['workshop_asst_mgr'] = UserSerializer(new_fields=['id', 'name', 'ops_phone', 'email'])
        return super(BookingSerializer, self).to_representation(obj)

    def get_bill_details(self, obj):
        return bookingManager.get_bill_details_new(obj)

    def get_payment_details(self, obj):
        return paymentManager.get_payment_details(obj)

    def get_eod_message(self, obj):
        return bookingManager.get_latest_eod_message(obj)

    # def get_payments(self, obj):
    #     return paymentManager.get_payments(obj)

    @classmethod
    def setup_eager_loading(cls, queryset, internal):
        """ Perform necessary eager loading of data. """
        from django.db.models import F
        queryset = queryset.select_related('status',
                                           'city',
                                           'ops_status',
                                           'pickup_driver',
                                           'drop_driver',
                                           'workshop_manager',
                                           'return_reason',
                                           'user'
                                           ).prefetch_related(
                                                     'booking_address',
                                                     'booking_address__address',
                                                     'booking_checkpoint',
                                                     'booking_checkpoint__status',
                                                     'booking_discount',
                                                     'booking_invoice',
                                                     'booking_proforma_invoice',
                                                     'booking_flag',
                                                     'user__user_credit',
                                                      Prefetch(
                                                         'user__user_credittrx',
                                                          queryset=CreditTransaction.objects.filter(
                                                              entity=CreditTransaction.ENTITY_BOOKING,
                                                              trans_type=CreditTransaction.TRANSACTION_TYPE_DEBIT,
                                                          )
                                                      ),
                                                      Prefetch(
                                                        "booking_invoice__invoice_payment",
                                                        queryset=Payment.objects.filter(
                                                                    payment_for=Payment.PAYMENT_FOR_USER,
                                                                    ).order_by('-id'),
                                                        to_attr='payments'
                                                        ),
                                                      Prefetch(
                                                        "booking_proforma_invoice__proforma_invoice_payment",
                                                        queryset=Payment.objects.filter(
                                                                    payment_for=Payment.PAYMENT_FOR_USER,
                                                                    ).order_by('-id'),
                                                        to_attr='proforma_payments'
                                                        ),
                                                      'booking_coupon',
                                                      'booking_coupon__coupon',
                                                      'booking_rework',
                                                      Prefetch(
                                                          'message_booking',
                                                          queryset=Messages.objects.filter(
                                                              label=Messages.LABEL_EOD).order_by('-created_at')
                                                        )
                                                     )
        if internal:
            queryset = queryset.prefetch_related('booking_package',
                                                 'booking_package__booking_package_panel',
                                                 'booking_package__booking_package_panel__panel',
                                                 'booking_package__booking_package_panel__panel__car_panel',
                                                 'booking_package__package',
                                                 'booking_package__package__package',)
        else:
            queryset = queryset.prefetch_related(Prefetch('booking_package',
                                                          queryset=BookingPackage.objects.filter(package__package__internal=False).prefetch_related(
                                                                Prefetch('booking_package_panel',
                                                                         queryset=BookingPackagePanel.objects.filter(panel__car_panel__internal=False,
                                                                                                                     panel__internal=False).prefetch_related(
                                                                            'panel',
                                                                            'panel__car_panel',
                                                                         )
                                                                ),
                                                                'package',
                                                                'package__package'),
                                                          ),
                                                 )
        return queryset

    def create(self, validated_data):
        return bookingManager.create_booking(validated_data)

    def update(self, instance, validated_data):
        return bookingManager.update_booking(instance, validated_data)

    def save(self, **kwargs):
        request = self.context['request']
        kwargs['updated_by'] = request.user
        kwargs['device_type'] = request.META.get('HTTP_SOURCE')
        super(BookingSerializer, self).save(**kwargs)


class GetSlotSerializer(serializers.Serializer):
    car_model = serializers.IntegerField(write_only=True, required=False)
    type = serializers.ChoiceField(write_only=True, required=True, choices=BookingAddress.ADDRESS_TYPES)
    is_doorstep = serializers.BooleanField(write_only=True, required=False)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.filter(active=True), required=False)


class BookingFollowupSerializer(DynamicFieldsModelSerializer):
    followup = FollowupSerializer(many=True)
    class Meta:
        model = Booking
        fields = ('id','followup','assigned_to','next_followup')

    def update(self, instance, validated_data):
        return bookingManager.update_followup(instance, validated_data)

    def save(self, **kwargs):
        request = self.context.get('request')
        kwargs['updated_by'] = request.user
        super(BookingFollowupSerializer, self).save(**kwargs)

    @classmethod
    def setup_eager_loading(cls, queryset, internal):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(Prefetch(
                                                'followup',
                                                Followup.objects.order_by('-created_at').select_related('updated_by',
                                                                                                        'result'),
                                            ))
        return queryset


class InitiatePaymentSerializer(serializers.Serializer):
    payment_type = serializers.ChoiceField(choices=Payment.PAYMENT_TYPES)
    amount = serializers.DecimalField(max_digits=10,decimal_places=2,min_value=0,required=False)


class ProcessPaymentSerializer(serializers.Serializer):
    vendor_id = serializers.CharField()
    payment_id = serializers.IntegerField(required=False)
    net_amount_debit = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    status = serializers.CharField()
    vendor_status = serializers.CharField(required=False)
    error_message = serializers.CharField(required=False)
    vendor = serializers.ChoiceField(choices=Payment.VENDOR_LIST)
    vendor_tx_data = serializers.CharField(required=False)
    mode = serializers.ChoiceField(choices=Payment.PAYMENT_MODES)
    payment_type = serializers.ChoiceField(choices=Payment.PAYMENT_TYPES, required=False)
    cheque_num = serializers.CharField(max_length=20, required=False)
    cheque_bank = serializers.CharField(max_length=32, required=False)
    tx_type = serializers.ChoiceField(choices=Payment.TX_TYPES, required=False)
    used_credits = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False)


class CouponDetailSerializer(serializers.Serializer):
    coupon_code = serializers.CharField()


class DriverBookingSerializer(serializers.ModelSerializer):
    booking_package = BookingPackageSerializer(many=True, remove_fields=['booking'],
                                               change_serializer={
                                                   'booking_package_panel': BookingPackagePanelSerializer(
                                                       remove_fields=['booking_package'],
                                                       many=True,
                                                       required=False)},
                                               required=False)
    booking_address = BookingAddressSerializer(many=True, remove_fields=['booking'],required=False)
    bill_details = serializers.SerializerMethodField()
    payment_details = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True, remove_fields=['referral'])
    status = BookingStatusSerializer(read_only=True)
    ops_status = BookingOpsStatusSerializer(read_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False)
    action = serializers.IntegerField(write_only=True,required=False)
    pickup_driver_details = UserSerializer(read_only=True, source='pickup_driver',
                                           new_fields=['name', 'email', 'phone', 'ops_phone'])
    drop_driver_details = UserSerializer(read_only=True, source='drop_driver',
                                         new_fields=['name', 'email', 'phone', 'ops_phone'])
    workshop_manager_details = UserSerializer(read_only=True, source='workshop_manager',
                                              new_fields=['name', 'email', 'phone', 'ops_phone'])
    workshop_details = WorkshopSerializer(read_only=True, source='workshop')
    usercar_details = UserCarSerializer(source='usercar', read_only=True, remove_fields=['active_bookings'])
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), source='user', write_only=True, required=False)
    payments = PaymentSerializer(many=True,
                                 remove_fields=[
                                                'tx_data',
                                                'tx_type',
                                                'payment_for',
                                                'vendor',
                                                'payment_vendor_id',
                                                'refund_vendor_id',
                                                'vendor_status',
                                                'cheque_num',
                                                'cheque_bank'],
                                 read_only=True)

    class Meta:
        model = Booking
        fields = ('__all__')

    def get_bill_details(self, obj):
        return bookingManager.get_bill_details_new(obj)

    def get_payment_details(self, obj):
        return paymentManager.get_payment_details(obj)

    @classmethod
    def setup_eager_loading(cls, queryset, internal):
        """ Perform necessary eager loading of data. """

        queryset = queryset.select_related('status',
                                           'city',
                                           'ops_status',
                                           'pickup_driver',
                                           'drop_driver',
                                           'workshop_manager',
                                           'workshop',
                                           'usercar',
                                           'user').prefetch_related('booking_address',
                                                                    'booking_address__address',
                                                                    'booking_package',
                                                                    'booking_package__booking_package_panel',
                                                                    'booking_package__booking_package_panel__panel',
                                                                    'booking_package__booking_package_panel__panel__car_panel',
                                                                    'booking_package__package',
                                                                    'booking_package__package__package',
                                                                    'booking_discount',
                                                                    'booking_invoice',
                                                                    'user__user_credit',
                                                                    'user__user_credittrx',
                                                                     Prefetch(
                                                                       "booking_invoice__invoice_payment",
                                                                        queryset=Payment.objects.filter(
                                                                            payment_for=Payment.PAYMENT_FOR_USER
                                                                            ).order_by('-id'),
                                                                        to_attr='payments'
                                                                        ),
                                                                     'booking_coupon'
                                                                     )

        return queryset

    def create(self, validated_data):
        return bookingManager.create_booking(validated_data)

    def update(self, instance, validated_data):
        return bookingManager.update_booking(instance, validated_data)

    def save(self, **kwargs):
        request = self.context['request']
        kwargs['updated_by'] = request.user
        kwargs['device_type'] = request.META.get('HTTP_SOURCE')
        super(DriverBookingSerializer, self).save(**kwargs)


class BookingImageSerializer(CreateListModelMixin, serializers.ModelSerializer):
    media = serializers.FileField(write_only=True, required=False)
    media_url = serializers.SerializerMethodField()
    image_name = serializers.CharField(write_only=True, required=False)
    size = serializers.IntegerField(write_only=True, required=False)
    content_type = serializers.CharField(write_only=True, required=False)
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                    queryset=get_user_model().objects.all())

    class Meta:
        model = BookingImage
        fields = '__all__'

    def to_representation(self, obj):
        self.fields['updated_by'] = UserSerializer(
                                        read_only=True,
                                        new_fields=['id','name','phone','ops_phone'])
        self.fields['status'] = BookingStatusSerializer(read_only=True)
        self.fields['ops_status'] = BookingOpsStatusSerializer(read_only=True)
        self.fields['panel'] = CarPanelSerializer(new_fields=['id', 'name'], read_only=True)
        return super(BookingImageSerializer, self).to_representation(obj)

    def create(self, validated_data):
        return bookingManager.create_booking_image(validated_data)

    def get_media_url(self, obj):
        request = self.context['request']
        return bookingManager.get_media_url(request, obj.media)


class BookingDiscountSerializer(serializers.ModelSerializer):
    reason_dd_details = DiscountReasonsSerializer(source='reason_dd',
                                                  read_only=True)
    class Meta:
        model = BookingDiscount
        fields = '__all__'

    def create(self, validated_data):
        bd_obj = super(BookingDiscountSerializer, self).create(validated_data)
        booking_invoices = bd_obj.booking.booking_invoice.filter(status__in=[BookingInvoice.INVOICE_STATUS_PENDING,
                                                                             BookingInvoice.INVOICE_STATUS_PAID])
        if booking_invoices:
            bookingManager.save_invoice(bd_obj.booking)

        send_custom_notification_task.delay('OPS_ADD_DISCOUNT_EMAIL',
                                            {'booking': bd_obj.booking_id,
                                             'labour_discount': bd_obj.labour_discount,
                                             'material_discount': bd_obj.material_discount,
                                             'part_discount': bd_obj.part_discount,
                                             'reason': bd_obj.reason,
                                            })
        return bd_obj

    def update(self, instance, validated_data):
        bd_obj = super(BookingDiscountSerializer, self).update(instance, validated_data)
        booking_invoices = bd_obj.booking.booking_invoice.filter(status__in=[BookingInvoice.INVOICE_STATUS_PENDING,
                                                                             BookingInvoice.INVOICE_STATUS_PAID])
        if booking_invoices:
            bookingManager.save_invoice(bd_obj.booking)
        return bd_obj


class BookingCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingCoupon
        fields = '__all__'

    def create(self, validated_data):
        bc_obj = super(BookingCouponSerializer, self).create(validated_data)
        booking_invoices = bc_obj.booking.booking_invoice.filter(status__in=[BookingInvoice.INVOICE_STATUS_PENDING,
                                                                             BookingInvoice.INVOICE_STATUS_PAID])
        if booking_invoices:
            bookingManager.save_invoice(bc_obj.booking)

        return bc_obj

    def update(self, instance, validated_data):
        bc_obj = super(BookingCouponSerializer, self).update(instance, validated_data)
        booking_invoices = bc_obj.booking.booking_invoice.filter(status__in=[BookingInvoice.INVOICE_STATUS_PENDING,
                                                                             BookingInvoice.INVOICE_STATUS_PAID])
        if booking_invoices:
            bookingManager.save_invoice(bc_obj.booking)
        return bc_obj


class BookingListSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Booking
        fields = ('id','usercar','status')

    @classmethod
    def setup_eager_loading(cls, queryset, internal):
        """ Perform necessary eager loading of data. """
        return queryset


class BookingBillSerializerV2(serializers.ModelSerializer):
    # ye ek rakshas (complex) code hai.. Please do not touch it without knowledge..
    booking_package = BookingPackageSerializer(many=True, remove_fields=['booking'],
                                               change_serializer={
                                                   'package':PackagePriceSerializer(
                                                       read_only=True,
                                                       remove_fields=['id', 'city'],
                                                       change_serializer={
                                                           'package':PackageSerializer(
                                                               new_fields=[
                                                                   'name', 'category'])}),
                                                   'booking_package_panel':BookingPackagePanelSerializer(
                                                       remove_fields=['booking_package'],
                                                       change_serializer={'panel_details':
                                                           CarPanelPriceSerializer(
                                                               remove_fields=['id',
                                                                              'type_of_work_val',
                                                                              'updated_at',
                                                                              'created_at',
                                                                              'car_type',
                                                                              'car_model',
                                                                              'editable',
                                                                              'city'],
                                                               change_serializer={
                                                                    'car_panel': CarPanelSerializer(new_fields=['name'])
                                                               },
                                                               source='panel',
                                                               read_only=True)},
                                                       many=True,
                                                       required=False)},
                                               required=False)
    bill_details = serializers.SerializerMethodField()
    payment_details = serializers.SerializerMethodField()
    user = UserSerializer(new_fields=['name','email','phone'])
    payment_gateway = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ('id','booking_package','bill_details','payment_details','usercar','user','payment_gateway')

    def get_bill_details(self, obj):
        return bookingManager.get_bill_details_new(obj)

    def get_payment_details(self, obj):
        return paymentManager.get_payment_details(obj)

    def get_payment_gateway(self, obj):
        return getattr(settings,'PAYMENT_GATEWAY_TO_USE', 1)

    @classmethod
    def setup_eager_loading(cls, queryset):
        """ Perform necessary eager loading of data. """

        queryset = queryset.select_related('user').prefetch_related(
                                             'booking_discount',
                                             'booking_invoice',
                                             'booking_proforma_invoice',
                                             'user__user_credit',
                                             'user__user_credittrx',
                                              Prefetch(
                                                "booking_invoice__invoice_payment",
                                                queryset=Payment.objects.filter(payment_for=Payment.PAYMENT_FOR_USER,
                                                                                ).order_by('-id'),
                                                to_attr='payments'
                                                ),
                                              Prefetch(
                                                "booking_proforma_invoice__proforma_invoice_payment",
                                                queryset=Payment.objects.filter(payment_for=Payment.PAYMENT_FOR_USER,
                                                                                    ).order_by('-id'),
                                                to_attr='proforma_payments'
                                                ),
                                              'booking_coupon',
                                              'booking_coupon__coupon'
                                             )
        queryset = queryset.prefetch_related('booking_package',
                                             'booking_package__booking_package_panel',
                                             'booking_package__booking_package_panel__panel',
                                             'booking_package__booking_package_panel__panel__car_panel',
                                             'booking_package__package',
                                             'booking_package__package__package',)
        return queryset


class BookingCartSerializer(serializers.ModelSerializer):
    booking_package = BookingPackageSerializer(many=True, remove_fields=['booking'],
                                               change_serializer={
                                                   'booking_package_panel':BookingPackagePanelSerializer(
                                                       remove_fields=['booking_package'],
                                                       many=True,
                                                       required=False)},
                                               required=False)
    bill_details = serializers.SerializerMethodField()
    payment_details = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ('__all__')

    def get_bill_details(self, obj):
        return bookingManager.get_bill_details_new(obj)

    def get_payment_details(self, obj):
        return paymentManager.get_payment_details(obj)

    @classmethod
    def setup_eager_loading(cls, queryset, internal):
        """ Perform necessary eager loading of data. """

        queryset = queryset.prefetch_related(
                                             'booking_discount',
                                             'booking_invoice',
                                             'booking_proforma_invoice',
                                             'user__user_credit',
                                             'user__user_credittrx',
                                              Prefetch(
                                                "booking_invoice__invoice_payment",
                                                queryset=Payment.objects.filter(payment_for=Payment.PAYMENT_FOR_USER,
                                                                                ).order_by('-id'),
                                                to_attr='payments'
                                                ),
                                              Prefetch(
                                                    "booking_proforma_invoice__proforma_invoice_payment",
                                                    queryset=Payment.objects.filter(payment_for=Payment.PAYMENT_FOR_USER,
                                                                                    ).order_by('-id'),
                                                    to_attr='proforma_payments'
                                                ),
                                              'booking_coupon',
                                              'booking_coupon__coupon'
                                             )
        if internal:
            queryset = queryset.prefetch_related('booking_package',
                                                 'booking_package__booking_package_panel',
                                                 'booking_package__booking_package_panel__panel',
                                                 'booking_package__booking_package_panel__panel__car_panel',
                                                 'booking_package__package',
                                                 'booking_package__package__package',)
        else:
            queryset = queryset.prefetch_related(Prefetch('booking_package',
                                                          queryset=BookingPackage.objects.filter(package__package__internal=False).prefetch_related(
                                                                Prefetch('booking_package_panel',
                                                                         queryset=BookingPackagePanel.objects.filter(panel__car_panel__internal=False,
                                                                                                                     panel__internal=False).prefetch_related(
                                                                            'panel',
                                                                            'panel__car_panel',
                                                                         )
                                                                ),
                                                                'package',
                                                                'package__package'),
                                                          ),
                                                 )
        return queryset


class BookingFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingFeedback
        fields = '__all__'
        validators = [ObjectUserValidator('booking', 'Booking')]


class BookingCustFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingCustFeedback
        fields = '__all__'
        validators = [ObjectUserValidator('booking', 'Booking')]

    def create(self, validated_data):
        booking = validated_data.get('booking')
        instance = BookingCustFeedback.objects.filter(booking=booking).first()
        if instance:
            return super(BookingCustFeedbackSerializer, self).update(instance, validated_data)
        return super(BookingCustFeedbackSerializer,self).create(validated_data)


class EODNoticeSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=list(ACTION_DICT.keys()), required=True)


class BookingProformaInvoiceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = BookingProformaInvoice
        fields = '__all__'
        validators = [ObjectUserValidator('booking', 'Booking')]

    def create(self, validated_data):
        bookingManager.validate_proforma_invoice(validated_data)
        return super(BookingProformaInvoiceSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(BookingProformaInvoiceSerializer, self).update(instance, validated_data)


class SaveEODSerializer(serializers.Serializer):
    message_type = serializers.ChoiceField(choices=Messages.MESSAGE_TYPES, required=True)
    message = serializers.CharField(max_length=4096, required=True)
    action = serializers.ChoiceField(choices=list(ACTION_DICT.keys()), required=False)


# class BookingReworkSerializer(serializers.ModelSerializer):
#     booking_package = BookingPackageSerializer(many=True, remove_fields=['booking',],
#                                                change_serializer={
#                                                    'booking_package_panel':BookingPackagePanelSerializer(
#                                                        remove_fields=['booking_package'],
#                                                        many=True,
#                                                        read_only=True)},
#                                                read_only=True)
#
#     class Meta:
#         model = Booking
#         fields = ('__all__')
#
#     @classmethod
#     def setup_eager_loading(cls, queryset, internal):
#         """ Perform necessary eager loading of data. """
#
#         queryset = queryset.prefetch_related('booking_package',
#                                              'booking_package__booking_package_panel',
#                                              'booking_package__booking_package_panel__panel',
#                                              'booking_package__booking_package_panel__panel__car_panel',
#                                              'booking_package__package',
#                                              'booking_package__package__package',
#                                              'booking_package__rework_package',
#                                              'booking_package__booking_package_panel__rework_panel')
#         return queryset


class BookingReworkPackagePanelSerializer(ConflictAwareModelSerializer):
    panel_details = BookingPackagePanelSerializer(read_only=True, source='booking_package_panel')

    class Meta:
        model = BookingReworkPackagePanel
        fields = '__all__'

    def create(self, validated_data):
        booking_package_panel = validated_data.get('booking_package_panel')
        obj = super(BookingReworkPackagePanelSerializer, self).create(validated_data)
        booking_package_panel.rework = True
        booking_package_panel.save()
        return obj


class BookingReworkPackageSerializer(ConflictAwareModelSerializer):
    booking_package_details = BookingPackageSerializer(read_only=True,source='booking_package',
                                                       remove_fields=['booking_package_panel'])
    class Meta:
        model = BookingReworkPackage
        fields = '__all__'

    def create(self, validated_data):
        booking_package = validated_data.get('booking_package')
        obj = super(BookingReworkPackageSerializer, self).create(validated_data)
        booking_package.rework = True
        booking_package.save()
        return obj


class WorkshopBookingSerializer(serializers.ModelSerializer):
    usercar_details = UserCarSerializer(source='usercar', read_only=True, remove_fields=['active_bookings'])
    status = BookingStatusSerializer(read_only=True)
    ops_status = BookingOpsStatusSerializer(read_only=True)
    booking_package = BookingPackageSerializer(many=True, remove_fields=['booking'],
                                               change_serializer={
                                                   'booking_package_panel': BookingPackagePanelSerializer(
                                                       remove_fields=['booking_package'],
                                                       many=True,
                                                       required=False)},
                                               required=False, read_only=True)
    last_updated_since = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ('__all__')

    def get_last_updated_since(self, booking):
        # return timezone.now()
        last_rec = booking.history.filter(
                        updated_by__groups__name='WorkshopExecutive').order_by('-updated_at').first()
        if last_rec:
            return last_rec.updated_at
        return None

    @classmethod
    def setup_eager_loading(cls, queryset, internal):
        """ Perform necessary eager loading of data. """

        return queryset.select_related('usercar',
                                       'status',
                                       'ops_status').prefetch_related(
                                                        'booking_package',
                                                        'booking_package__booking_package_panel',
                                                        'booking_package__booking_package_panel__panel',
                                                        'booking_package__booking_package_panel__panel__car_panel',
                                                        'booking_package__package',
                                                        'booking_package__package__package')

    def create(self, validated_data):
        return bookingManager.create_booking(validated_data)

    def update(self, instance, validated_data):
        return bookingManager.update_booking(instance, validated_data)

    def save(self, **kwargs):
        request = self.context['request']
        kwargs['updated_by'] = request.user
        kwargs['device_type'] = request.META.get('HTTP_SOURCE')
        super(WorkshopBookingSerializer, self).save(**kwargs)


class BookingQualityCheckSerializer(serializers.ModelSerializer):
    quality_check = QualityCheckSerializer(read_only=True)

    class Meta:
        model = BookingQualityChecks
        exclude = ('booking',)


class BookingTestedQualityCheckSerializer(serializers.Serializer):
    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all(), required=True)
    checked_items = serializers.ListField(child=TestedQualityCheckSerializer())
    #qc_image = BookingImageSerializer(required=False)

    def create(self, validated_data):
        # :-)
        # if not Booking.objects.filter(id=validated_data.get('booking_id')).exists():
        #     raise serializers.ValidationError("Invalid Booking Id.")
        #
        # booking = Booking.objects.get(id=validated_data.get('booking_id'))
        booking = validated_data.get('booking')
        bookingManager.create_qc_checks(booking, validated_data)


class EntityChangeTrackerSerializer(serializers.ModelSerializer):
    delay_reason_details = DelayReasonsSerializer(read_only=True, source='delay_reason')
    updated_by_details = UserSerializer(source='updated_by',
                                        read_only=True,
                                        remove_fields=['groups','user_credit','city','active_devices','user_detail',
                                                       'referral'])
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(), write_only=True,
                                                    queryset=get_user_model().objects.all())
    class Meta:
        model = EntityChangeTracker
        fields = ('__all__')


class TeamAlertSerializer(serializers.ModelSerializer):
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                    queryset=get_user_model().objects.all())
    reason_details = TeamAlertReasonSerializer(source='alert_reason', read_only=True,
                                               new_fields=['reason', 'reason_type'])

    class Meta:
        model = TeamAlert
        fields = ('__all__')


class BookingHandoverSerializer(serializers.ModelSerializer):
    item = HandoverItemSerializer(read_only=True)

    class Meta:
        model = BookingHandoverItem
        exclude = ('booking',)


class BookingHandoverCreateSerializer(serializers.Serializer):
    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all(), required=True)
    item_list = serializers.ListField(child=BookingHandoverItemCreateSerializer())

    def create(self, validated_data):
        booking = validated_data.get('booking')
        return bookingManager.create_handover_list(booking, validated_data)


class BookingChecklistSerializer(serializers.ModelSerializer):
    item = ChecklistItemSerializer(read_only=True)
    media = MediaSerializer(read_only=True, many=True, new_fields=['media_url'])
    updated_by_details = UserSerializer(source='updated_by',
                                        read_only=True,
                                        new_fields=['id', 'name', 'email', 'phone', 'ops_phone'])

    class Meta:
        model = BookingChecklist
        exclude = ('booking',)


class BookingChecklistCreateSerializer(serializers.Serializer):
    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all(), required=True)
    item_list = serializers.ListField(child=BookingChecklistItemCreateSerializer())

    class Meta:
        validators = [ObjectUserValidator('booking', 'Booking')]

    def create(self, validated_data):
        booking = validated_data.get('booking')
        return bookingManager.create_checklist(booking, validated_data)


class PartQuoteNoteSerializer(DynamicFieldsModelSerializer):
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                    queryset=get_user_model().objects.all())
    class Meta:
        model = PartQuoteNote
        fields = '__all__'

    def to_representation(self, obj):
        self.fields['updated_by'] = UserSerializer(
            read_only=True,
            new_fields=['id', 'name', 'phone', 'ops_phone'])
        return super(PartQuoteNoteSerializer, self).to_representation(obj)


class BookingPartQuoteSerializer(DynamicFieldsModelSerializer):
    notes = PartQuoteNoteSerializer(many=True, required=False)

    class Meta:
        model = BookingPartQuote
        fields = '__all__'

    def to_representation(self, obj):
        if self.fields.get('vendor'):
            serializer_class = GenericModelSerializer
            serializer_class.Meta.model = PartVendor
            self.fields['vendor'] = serializer_class(new_fields=['id', 'name', 'city'])
        return super(BookingPartQuoteSerializer, self).to_representation(obj)

    def create(self, validated_data):
        notes = validated_data.pop('notes', [])
        instance = super(BookingPartQuoteSerializer, self).create(validated_data)
        for note in notes:
            #note['updated_by'] = validated_data.get('updated_by')
            note_obj = PartQuoteNote.objects.create(**note)
            instance.notes.add(note_obj)
        return instance

    def update(self, instance, validated_data):
        notes = validated_data.pop('notes', [])
        instance = super(BookingPartQuoteSerializer, self).update(instance, validated_data)
        for note in notes:
            #note['updated_by'] = validated_data.get('updated_by')
            note_obj = PartQuoteNote.objects.create(**note)
            instance.notes.add(note_obj)
        if instance.selected:
            booking_part = instance.booking_part_doc.booking_part
            booking_part.part_price = instance.price
            booking_part.save()
        return instance


class PartDocNoteSerializer(DynamicFieldsModelSerializer):
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                    queryset=get_user_model().objects.all())
    class Meta:
        model = PartDocNote
        fields = '__all__'

    def to_representation(self, obj):
        self.fields['updated_by'] = UserSerializer(
            read_only=True,
            new_fields=['id', 'name', 'phone', 'ops_phone'])
        return super(PartDocNoteSerializer, self).to_representation(obj)


class BookingPartDocSerializer(DynamicFieldsModelSerializer):
    notes = PartDocNoteSerializer(many=True, required=False)
    booking_part_quote = BookingPartQuoteSerializer(many=True, read_only=True)

    class Meta:
        model = BookingPartDoc
        fields = '__all__'

    def to_representation(self, obj):
        if self.fields.get('status'):
            status_serializer_class = GenericModelSerializer
            status_serializer_class.Meta.model = PartDocStatus
            self.fields['status'] = status_serializer_class(new_fields=['id', 'name'])
        self.fields['booking_part'] = BookingPackagePanelSerializer(
                                        read_only=True,
                                        new_fields=['id', 'panel_details'],
                                        change_serializer={
                                            'panel_details': CarPanelPriceSerializer(
                                                                source='panel',
                                                                new_fields=['car_panel'],
                                                                change_serializer={
                                                                    'car_panel': CarPanelSerializer(
                                                                                    new_fields=['name'])
                                                                })
                                        })
        return super(BookingPartDocSerializer, self).to_representation(obj)

    def create(self, validated_data):
        notes = validated_data.pop('notes', [])
        instance = super(BookingPartDocSerializer, self).create(validated_data)
        for note in notes:
            # note['updated_by'] = validated_data.get('updated_by')
            note_obj = PartDocNote.objects.create(**note)
            instance.notes.add(note_obj)
        return instance

    def update(self, instance, validated_data):
        notes = validated_data.pop('notes', [])
        instance = super(BookingPartDocSerializer, self).update(instance, validated_data)
        for note in notes:
            # note['updated_by'] = validated_data.get('updated_by')
            note_obj = PartDocNote.objects.create(**note)
            instance.notes.add(note_obj)
        return instance


class BPPHistorySerializer(DynamicFieldsModelSerializer):
    # Booking package panel history serializer
    panel = CarPanelPriceSerializer(new_fields=['car_panel', 'type_of_work'],
                                    change_serializer={
                                        'car_panel': CarPanelSerializer(
                                                        new_fields=['name'])
                                    })

    class Meta:
        model = BookingPackagePanel.history.model
        fields = ('id', 'history_id', 'updated_at', 'created_at', 'booking_package', 'history_type',
                  'panel', 'part_price', 'material_price', 'labour_price')


class BookingExpectedEODSerializer(DynamicFieldsModelSerializer):
    updated_by = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(),
                                                    queryset=get_user_model().objects.all())
    ops_status_details = BookingOpsStatusSerializer(source='ops_status',read_only=True)
    updated_by_details = UserSerializer(source='updated_by',
                                        read_only=True,
                                        new_fields=['id', 'name', 'email', 'phone', 'ops_phone'])

    class Meta:
        model = BookingExpectedEOD
        fields = ('__all__')
