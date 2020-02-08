from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords
from core.models.common import CreatedAtAbstractBase, Address, Media
from core.models import master
from core.models import users
from core.models import incentive
from django.db.models import Q
from core.models.coupons import Coupon
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

import logging
logger = logging.getLogger(__name__)


class Booking(CreatedAtAbstractBase):
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
    SOURCE_ANDROID = 'android'
    SOURCE_IPHONE = 'iphone'
    SOURCE_FACEBOOK = 'facebook'
    SOURCE_REFERRAL = 'referral'
    SOURCE_JUSTDIAL = 'justdial'
    SOURCE_OPS_PANEL = 'opsPanel'
    SOURCE_DRWHEELZ = 'drwheelz'
    SOURCE_INCOMING_CALL = 'incomingCall'
    SOURCE_URBANCLAP = 'urbanClap'
    SOURCE_REWORK = 'rework'
    SOURCE_CARS24 = 'cars24'
    SOURCE_HP_PETROL_PUMP = 'hp'
    SOURCE_HELPSHIFT = 'helpshift'
    SOURCE_SULEKHA = 'sulekha'
    SOURCE_SCRATCH_FINDER = 'scratch-finder'

    BOOKING_SOURCES = (
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
        (SOURCE_ANDROID, 'android'),
        (SOURCE_IPHONE, 'iphone'),
        (SOURCE_FACEBOOK, 'Facebook'),
        (SOURCE_REFERRAL, 'Referral'),
        (SOURCE_JUSTDIAL, 'JustDial'),
        (SOURCE_OPS_PANEL, 'OpsPanel'),
        (SOURCE_DRWHEELZ, 'drwheelz'),
        (SOURCE_INCOMING_CALL, 'Incoming Call'),
        (SOURCE_URBANCLAP, 'UrbanClap'),
        (SOURCE_REWORK, 'Rework'),
        (SOURCE_CARS24, 'Cars 24'),
        (SOURCE_HP_PETROL_PUMP, 'HP Petrol Pump'),
        (SOURCE_HELPSHIFT, 'HelpShift'),
        (SOURCE_SULEKHA, 'Sulekha'),
        (SOURCE_SCRATCH_FINDER, 'Scratch-Finder'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='booking')
    usercar = models.ForeignKey(users.UserCar)
    source = models.ForeignKey(master.Source, blank=True, null=True, related_name='booking_sources',
                               db_column="source")
    status = models.ForeignKey(master.BookingStatus,related_name='booking_status')
    ops_status = models.ForeignKey(master.BookingOpsStatus, null=True, blank=True, related_name='booking_ops_status')
    city = models.ForeignKey(master.City)
    desc = models.CharField(max_length=2048, null=True, blank=True)
    pickup_time = models.DateTimeField(null=True, blank=True) #pickup time selected by user
    pickup_slot_end_time = models.DateTimeField(null=True, blank=True) #pickup time selected by user
    drop_time = models.DateTimeField(null=True, blank=True) #drop time selected by user
    drop_slot_end_time = models.DateTimeField(null=True, blank=True) #drop time selected by user
    pickup_driver_start_time = models.DateTimeField(null=True, blank=True) #driver started for pickup
    driver_arrived_pickup_time = models.DateTimeField(null=True, blank=True) #driver arrived at customer location for pickup
    actual_pickup_time = models.DateTimeField(null=True, blank=True)
    pickup_driver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='booking_pickup_driver',
                                      null=True, blank=True,on_delete=models.SET_NULL,
                                      limit_choices_to=Q(groups__name='Driver'))
    actual_pickup_address = models.CharField(max_length=256,null=True, blank=True)
    workshop_reached_time = models.DateTimeField(null=True, blank=True) #This is time when car reached workshop. Driver will mark this.
    estimate_work_start_time = models.DateTimeField(null=True, blank=True) # workshop manager will update when the work will be started on car.
    actual_work_start_time = models.DateTimeField(null=True, blank=True) # workshop manager will update when the work started.
    estimate_complete_time = models.DateTimeField(null=True, blank=True) #estimated completion time by bumper to cust when car will be ready.Customer ETA
    actual_work_end_time = models.DateTimeField(null=True, blank=True) # actual time when work is completed and car is ready to be dropped.
    drop_driver_start_time = models.DateTimeField(null=True, blank=True)  # driver started for drop
    driver_arrived_drop_time = models.DateTimeField(null=True, blank=True)
    actual_drop_time = models.DateTimeField(null=True, blank=True, help_text="Car delivered action time")
    actual_drop_address = models.CharField(max_length=256,null=True, blank=True)
    drop_driver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='booking_drop_driver', null=True, blank=True,on_delete=models.SET_NULL, limit_choices_to=Q(groups__name='Driver'))
    workshop = models.ForeignKey(master.Workshop, null=True, blank=True)
    workshop_manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='booking_workshop_manager', null=True,
                                         blank=True,on_delete=models.SET_NULL, limit_choices_to=Q(groups__name='WorkshopManager'))
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='booking_assigned_to', null=True, blank=True, limit_choices_to=Q(groups__name='OpsUser'))
    next_followup = models.DateTimeField(null=True, blank=True, help_text="Next Followup date.")
    cancel_reason_dd = models.ForeignKey(master.CancellationReasons, null=True, blank=True)
    reason_for_cancellation_desc = models.CharField(max_length=512, null=True, blank=True)
    final_cancel_reason = models.ForeignKey(master.CancellationReasons, null=True, blank=True,
                                            related_name="booking_final_cancel_reason")
    status_updated_at = models.DateTimeField(null=True, blank=True)
    last_status = models.ForeignKey(master.BookingStatus,related_name='booking_laststatus',null=True, blank=True)
    ops_status_updated_at = models.DateTimeField(null=True, blank=True)
    last_opsstatus = models.ForeignKey(master.BookingOpsStatus,related_name='booking_lastopsstatus',null=True, blank=True)
    is_doorstep = models.BooleanField(default=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='booking_updated_by',null=True,blank=True,on_delete=models.SET_NULL, limit_choices_to=Q(groups__name='OpsUser'))
    followup = models.ManyToManyField(users.Followup, related_name='booking_followup', blank=True)
    lead_quality = models.PositiveSmallIntegerField(null=True, blank=True, choices=users.UserInquiry.LEAD_QUALITIES)
    latitude = models.DecimalField(max_digits=11,decimal_places=8,null=True,blank=True) # to store the location info for action.
    longitude = models.DecimalField(max_digits=11,decimal_places=8,null=True,blank=True) # to store the location info for action.
    workshop_eta = models.DateTimeField(null=True, blank=True) #estimated completion time by workshop to bumper when car will be ready
    caller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='booking_caller', null=True, blank=True,
                               limit_choices_to=Q(groups__name='OpsUser'))
    rework_booking = models.ForeignKey('self', blank=True, null=True, related_name='booking_rework', help_text="if booking A is there and Booking B is reowork of it, then A's Id will be there in B.")
    delay_reason = models.ForeignKey(master.DelayReasons, blank=True, null=True, related_name='booking_delay_reason')
    return_reason = models.ForeignKey(master.CarReturnReasons, blank=True, null=True, related_name='booking_return_reason')
    workshop_executive = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='booking_workshop_executive', null=True,
                                           blank=True, on_delete=models.SET_NULL,
                                           limit_choices_to=Q(groups__name='WorkshopExecutive'))
    pick_drop_manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='booking_pick_drop_manager',
                                          null=True,
                                          blank=True, on_delete=models.SET_NULL,
                                          limit_choices_to=Q(groups__name='DriverManager'))
    return_wo_work = models.BooleanField(default=False)
    delivery_reason = models.ForeignKey(master.DeliveryReasons, related_name="booking_delivery_reason",
                                        null=True, blank=True)
    delivery_reason_desc = models.TextField(null=True, blank=True)
    workshop_asst_mgr = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="booking_workshop_asst_mgr",
                                          null=True, blank=True, on_delete=models.SET_NULL,
                                          limit_choices_to=Q(groups__name='WorkshopAssistantManager'))

    history = HistoricalRecords()

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return "%s" % self.id

    def __repr__(self):
        return "id:{}, status:{}, ops_status:{}".format(self.id, self.status_id, self.ops_status_id)

    def __init__(self, *args, **kwargs):
        super(Booking, self).__init__(*args, **kwargs)
        setattr(self, '__original_booking_status_id', self.status_id)
        setattr(self, '__original_booking_opsstatus_id', self.ops_status_id)
        setattr(self, '__orig_pickup_slot_end_time', self.pickup_slot_end_time)
        setattr(self, '__orig_drop_slot_end_time', self.drop_slot_end_time)
        #setattr(self, '__original_booking_status', self.status)

    def _get_new_and_old_status(self):
        return getattr(self, '__original_booking_status_id'), self.status_id

    def _get_new_and_old_opsstatus(self):
        return getattr(self, '__original_booking_opsstatus_id'), self.ops_status_id
    
    def _get_pickup_slot_end_time(self):
        return getattr(self, '__orig_pickup_slot_end_time'), self.pickup_slot_end_time
    
    def _get_drop_slot_end_time(self):
        return getattr(self, '__orig_drop_slot_end_time'), self.drop_slot_end_time

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        old_id = self.id
        old_status_id, new_status_id = self._get_new_and_old_status()
        # This is done because for creation time old and new status Id are both coming to 1.
        if not old_id:
            old_status_id = None

        from django.utils import timezone
        old_opsstatus_id, new_opsstatus_id = self._get_new_and_old_opsstatus()
        if str(old_status_id) != str(new_status_id):
            self.last_status_id = old_status_id
            if str(old_opsstatus_id) == str(new_opsstatus_id):
                self.ops_status_id = None
            self.status_updated_at = timezone.now()

        if str(old_opsstatus_id) != str(new_opsstatus_id):
            self.last_opsstatus_id = old_opsstatus_id
            self.ops_status_updated_at = timezone.now()

        old_drop_slot_end_time, new_drop_slot_end_time = self._get_drop_slot_end_time()
        if old_drop_slot_end_time == new_drop_slot_end_time and self.drop_time is not None:
            self.drop_slot_end_time = self.drop_time + timezone.timedelta(hours=1)
            #setattr(self, '__orig_drop_slot_end_time', self.drop_slot_end_time)

        old_pickup_slot_end_time, new_pickup_slot_end_time = self._get_pickup_slot_end_time()
        if old_pickup_slot_end_time == new_pickup_slot_end_time and self.pickup_time is not None:
            self.pickup_slot_end_time = self.pickup_time + timezone.timedelta(hours=1)
            #setattr(self, '__orig_pickup_slot_end_time', self.pickup_slot_end_time)

        super(Booking, self).save()

        if str(old_status_id) != str(new_status_id):
            logger.info("----booking id:%s, old_status:%s, new status:%s" % (self.id,old_status_id,new_status_id))
            old_status = None
            if old_status_id:
                old_status = master.BookingStatus.objects.filter(id=old_status_id).first()
            if old_status and old_status.is_checkpoint and self.pk is not None:
                BookingCheckpoint.objects.get_or_create(booking=self,status=old_status)
            setattr(self, '__original_booking_status_id', self.status_id)
            setattr(self, '__original_booking_opsstatus_id', self.ops_status_id)


class BookingPackage(CreatedAtAbstractBase): # Remember denting is also a package.
    booking = models.ForeignKey(Booking,related_name="booking_package")
    package = models.ForeignKey(master.PackagePrice)
    active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    #service_tax = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    #vat = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    part_price = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    material_price = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    labour_price = models.DecimalField(max_digits=10,decimal_places=2, null=True, blank=True)
    #part_vat = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    #material_vat = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    #labour_service_tax = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    #labour_kk_tax = models.DecimalField(max_digits=10,decimal_places=2,default=0)  # krishi kalyan tax wtf
    #labour_sb_tax = models.DecimalField(max_digits=10,decimal_places=2,default=0)  # swacch bharat tax wtf
    rework = models.BooleanField(default=False,
                                 help_text="Rework done on this package.")
    extra = models.BooleanField(default=False,
                                help_text="Is this package extra after rework.")

    history = HistoricalRecords()

    def __unicode__(self):
        return "%s-%s" % (self.booking.id, self.id)

    class Meta:
        unique_together = ('booking','package')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.price:
            self.price = self.package.price
        if self.part_price is None:
            self.part_price = self.package.part_price
        if self.material_price is None:
            self.material_price = self.package.material_price
        if self.labour_price is None:
            self.labour_price = self.package.labour_price
        super(BookingPackage, self).save()


class BookingPackagePanel(CreatedAtAbstractBase):
    """
    This table will keep the data for denting package. The panels chosen by the user.
    """
    booking_package = models.ForeignKey(BookingPackage, related_name='booking_package_panel')
    panel = models.ForeignKey(master.CarPanelPrice)
    price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    part_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    material_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    labour_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    rework = models.BooleanField(default=False,
                                 help_text="Rework done on this panel.")
    extra = models.BooleanField(default=False,
                                help_text="Is this panel extra after rework.")

    history = HistoricalRecords()

    def __unicode__(self):
        return "%s" % self.id

    class Meta:
        unique_together = ('booking_package','panel')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.price is None:
            self.price = self.panel.price
        if self.part_price is None:
            self.part_price = self.panel.part_price
        if self.material_price is None:
            self.material_price = self.panel.material_price
        if self.labour_price is None:
            self.labour_price = self.panel.labour_price
        super(BookingPackagePanel, self).save()


class BookingAddress(CreatedAtAbstractBase):
    ADDRESS_TYPE_PICKUP = 1
    ADDRESS_TYPE_DROP = 2
    ADDRESS_TYPES = (
        (ADDRESS_TYPE_PICKUP,'Pickup'),
        (ADDRESS_TYPE_DROP,'Drop'),
    )

    booking = models.ForeignKey(Booking,related_name="booking_address")
    type = models.PositiveSmallIntegerField(choices=ADDRESS_TYPES)
    address = models.ForeignKey(Address)
    useraddress = models.ForeignKey(users.UserAddress, null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.id


class BookingDiscount(CreatedAtAbstractBase):
    PAYMENT_STATUS_PENDING = 'Pending Payment'
    PAYMENT_STATUS_PAID = 'Paid'
    PAYMENT_STATUS_PAID_EXCESS = 'Paid in Excess'

    booking = models.ForeignKey(Booking,related_name='booking_discount')
    labour_discount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    material_discount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    part_discount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    reason = models.CharField(max_length=2048)
    reason_dd = models.ForeignKey(master.DiscountReasons, null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.id

    @staticmethod
    def get_field_names():
        fnames = BookingDiscount._meta.get_all_field_names()
        return fnames


# class BillItem(CreatedAtAbstractBase):
#     bill = models.ForeignKey(BookingBill,related_name='bill_items')
#     package = models.ForeignKey(master.PackagePrice)
#     amount = models.DecimalField(max_digits=10,decimal_places=2)
#     service_tax = models.DecimalField(max_digits=10,decimal_places=2,default=0)
#     vat = models.DecimalField(max_digits=10,decimal_places=2,default=0)
#
#     def __unicode__(self):
#         return "%s" % self.id


class BookingCheckpoint(CreatedAtAbstractBase):
    booking = models.ForeignKey(Booking,related_name='booking_checkpoint')
    status = models.ForeignKey(master.BookingStatus)

    def __unicode__(self):
        return "%s" % self.id


class BookingAlertTriggerStatus(CreatedAtAbstractBase):
    # TRIGGER_PICKUP_IN_1_HR = 1
    # TRIGGER_DROP_IN_6_HR = 2
    # TRIGGER_WORK_NOT_COMPLETE_DROP_IN_1_HR = 3
    #
    # TRIGGER_TYPES = (
    #     (TRIGGER_PICKUP_IN_1_HR, 'PICKUP_IN_1_HR'),
    #     (TRIGGER_DROP_IN_6_HR, 'DROP_IN_6_HR'),
    #     (TRIGGER_WORK_NOT_COMPLETE_DROP_IN_1_HR, 'WORK_NOT_COMPLETE_DROP_IN_1_HR'),
    # )
    booking = models.ForeignKey(Booking,related_name='bookingTrigger')
    #trigger = models.SmallIntegerField(choices=TRIGGER_TYPES, null=True)
    is_triggered = models.BooleanField(default=True, help_text="if already triggered then value will be true.")
    alert_type = models.ForeignKey(master.OpsAlertType, null=True, blank=True)

    def __str__(self):
        return "%s" % self.id

    def __unicode__(self):
        return "%s" % self.id


@python_2_unicode_compatible
class BookingCoupon(CreatedAtAbstractBase):
    coupon = models.ForeignKey(Coupon)
    booking = models.ForeignKey(Booking,related_name="booking_coupon") # booking for which coupon is used.
    discount = models.DecimalField(max_digits=10,decimal_places=2, default=0,
                                   help_text=_("This is the cash discount given for coupon."))
    cashback = models.DecimalField(max_digits=10,decimal_places=2, default=0,
                                   help_text=_("This is the cashback given for coupon."))
    is_paid = models.BooleanField(default=False, help_text=_("Coupon will be used only if payment is made."))

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("BookingCoupon")
        verbose_name_plural = _("BookingCoupons")

    def __str__(self):
        return "%s-%s" % (self.coupon,self.booking)


class BookingImage(CreatedAtAbstractBase):
    JOBCARD_DRIVER = 1
    JOBCARD_INSPECTION = 2
    JOBCARD_WORKSHOP = 3

    JOBCARD_TYPES = (
        (JOBCARD_DRIVER, "Prepared By Driver"),
        (JOBCARD_INSPECTION, "Prepared After Inspection"),
        (JOBCARD_WORKSHOP, "Prepared by Workshop"),
    )

    IMAGE_TYPE_JOBCARD = 1
    IMAGE_TYPE_HANDOVER_SHEET_PICKUP = 2
    IMAGE_TYPE_CAR_PHOTO = 3
    IMAGE_TYPE_INSPECTION_SHEET = 4
    IMAGE_TYPE_HANDOVER_SHEET_DROP = 5
    IMAGE_TYPE_DURING_QUALITY_CHECK = 6

    IMAGE_TYPES = (
        (IMAGE_TYPE_JOBCARD, "Jobcard"),
        (IMAGE_TYPE_HANDOVER_SHEET_PICKUP, "Handover Crew To WS Sheet"),
        (IMAGE_TYPE_INSPECTION_SHEET, "Inspection Sheet"),
        (IMAGE_TYPE_CAR_PHOTO, "Car Photo"),
        (IMAGE_TYPE_HANDOVER_SHEET_DROP, "Handover WS To Crew Sheet"),
        (IMAGE_TYPE_DURING_QUALITY_CHECK, "During Quality Check"),
    )

    booking = models.ForeignKey(Booking, related_name='booking_image')
    media = models.ForeignKey(Media, related_name='booking_image_media')
    jobcard_type = models.PositiveSmallIntegerField(choices=JOBCARD_TYPES, null=True)
    image_type = models.PositiveSmallIntegerField(choices=IMAGE_TYPES, default=IMAGE_TYPE_JOBCARD)
    panel = models.ForeignKey(master.CarPanel, null=True, blank=True)
    status = models.ForeignKey(master.BookingStatus, null=True, blank=True)
    ops_status = models.ForeignKey(master.BookingOpsStatus, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return "%s" % self.media

    def __unicode__(self):
        return "%s" % self.media


class BookingInvoice(CreatedAtAbstractBase):
    INVOICE_STATUS_PENDING = 1
    INVOICE_STATUS_CANCELLED = 2
    INVOICE_STATUS_PAID = 3

    INVOICE_STATUSES = (
        (INVOICE_STATUS_PENDING, "Pending"),
        (INVOICE_STATUS_CANCELLED, "Cancelled"),
        (INVOICE_STATUS_PAID, "Paid")
    )

    booking = models.ForeignKey(Booking, related_name='booking_invoice')
    status = models.PositiveSmallIntegerField(choices=INVOICE_STATUSES)
    payable_amt = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    amt_wo_discount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    labour_price = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    part_price = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    material_price = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    vat = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    service_tax = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    kk_tax = models.DecimalField(max_digits=10,decimal_places=2,default=0)  # krishi kalyan tax wtf
    sb_tax = models.DecimalField(max_digits=10,decimal_places=2,default=0)  # swacch bharat tax wtf
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    igst = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return "%s" % self.id


class BookingFeedback(CreatedAtAbstractBase):
    HAPPINESS_RATING_NOTHAPPY = 1
    HAPPINESS_RATING_LOVEDIT = 2

    HAPPINESS_RATINGS = (
        (HAPPINESS_RATING_NOTHAPPY, "Not Happy"),
        (HAPPINESS_RATING_LOVEDIT, "Loved It")
    )

    booking = models.ForeignKey(Booking, related_name='booking_feedback')
    bumper_app = models.PositiveSmallIntegerField(choices=HAPPINESS_RATINGS)
    customer_care = models.PositiveSmallIntegerField(choices=HAPPINESS_RATINGS)
    work_quality = models.PositiveSmallIntegerField(choices=HAPPINESS_RATINGS)
    value_for_money = models.PositiveSmallIntegerField(choices=HAPPINESS_RATINGS)
    pick_drop_service = models.PositiveSmallIntegerField(choices=HAPPINESS_RATINGS)
    wow_moment = models.CharField(max_length=2048, null=True, blank=True)
    any_suggestions = models.CharField(max_length=2048, null=True, blank=True)
    feedback_remarks = models.CharField(max_length=2048)
    customer_issue = models.CharField(max_length=2048, null=True, blank=True)
    customer_relation_remarks = models.CharField(max_length=2048, null=True, blank=True)
    referrals = models.CharField(max_length=2048, null=True, blank=True)
    experience_rating = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return "%s" % self.id


class BookingCustFeedback(CreatedAtAbstractBase):
    RATING_VERY_UNHAPPY = 1
    RATING_UNHAPPY = 2
    RATING_NEUTRAL = 3
    RATING_HAPPY = 4
    RATING_VERY_HAPPY = 5

    RATINGS = (
        (RATING_VERY_UNHAPPY, "Very UnHappy"),
        (RATING_UNHAPPY, "UnHappy"),
        (RATING_NEUTRAL, "Neutral"),
        (RATING_HAPPY, "Happy"),
        (RATING_VERY_HAPPY, "Very Happy"),
    )

    booking = models.ForeignKey(Booking, related_name='booking_cust_feedback')
    booking_experience = models.PositiveSmallIntegerField(choices=RATINGS, null=True, blank=True)
    customer_care = models.PositiveSmallIntegerField(choices=RATINGS, null=True, blank=True)
    work_quality = models.PositiveSmallIntegerField(choices=RATINGS, null=True, blank=True)
    value_for_money = models.PositiveSmallIntegerField(choices=RATINGS, null=True, blank=True)
    pickup_experience = models.PositiveSmallIntegerField(choices=RATINGS, null=True, blank=True)
    any_suggestions = models.CharField(max_length=2048, null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.id


class BookingOpsAlerts(CreatedAtAbstractBase):
    ALERT_PENDING = 1
    ALERT_SENT = 2
    ALERT_CANCELLED = 3

    ALERT_CHOICES = (
        (ALERT_PENDING, "Pending"),
        (ALERT_SENT, "Sent"),
        (ALERT_CANCELLED, "Cancelled"),
    )

    booking = models.ForeignKey(Booking, related_name='booking_opsalert')
    alert_type = models.ForeignKey(master.OpsAlertType)
    time_to_send = models.DateTimeField(null=False, blank=False)
    alert_status = models.PositiveSmallIntegerField(choices=ALERT_CHOICES, default=ALERT_PENDING)

    def __unicode__(self):
        return "%s" % self.id


class BookingProformaInvoice(CreatedAtAbstractBase):
    INVOICE_STATUS_PENDING = 1
    INVOICE_STATUS_CANCELLED = 2
    INVOICE_STATUS_PAID = 3

    INVOICE_STATUSES = (
        (INVOICE_STATUS_PENDING, "Pending"),
        (INVOICE_STATUS_CANCELLED, "Cancelled"),
        (INVOICE_STATUS_PAID, "Paid")
    )

    booking = models.ForeignKey(Booking, related_name='booking_proforma_invoice')
    status = models.PositiveSmallIntegerField(choices=INVOICE_STATUSES, default=INVOICE_STATUS_PENDING)
    payable_amt = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    note = models.CharField(max_length=2048)

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return "%s" % self.id


class BookingReworkPackage(CreatedAtAbstractBase):
    booking_package = models.ForeignKey(BookingPackage,related_name="rework_package")
    reason = models.CharField(max_length=1024,
                              help_text="Reason for rework")

    def __unicode__(self):
        return "%s" % self.id


class BookingReworkPackagePanel(CreatedAtAbstractBase):
    # Scenario where we need to charge extra money from customer with rework on same panel.
    booking_package_panel = models.ForeignKey(BookingPackagePanel,related_name="rework_panel")
    type_of_work = models.PositiveSmallIntegerField(choices=master.CarPanelPrice.TYPE_OF_WORKS)
    reason = models.CharField(max_length=1024,
                              help_text="Reason for rework")

    def __unicode__(self):
        return "%s" % self.id


class BookingQualityChecks(CreatedAtAbstractBase):
    booking = models.ForeignKey(Booking, related_name="booking_quality_check")
    quality_check = models.ForeignKey(master.QualityCheck)
    is_passed = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=1024, null=True, blank=True)
    booking_image = models.ForeignKey(BookingImage, related_name="booking_qc_images", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bqc_updated_by")
    group_num = models.IntegerField(default=1)

    def __unicode__(self):
        return "%s" % self.id


class BookingHandoverItem(CreatedAtAbstractBase):
    booking = models.ForeignKey(Booking, related_name="booking_handover_item")
    item = models.ForeignKey(master.HandoverItem)
    has_issue = models.BooleanField(default=False)
    is_applicable = models.BooleanField(default=True)
    issue_reason = models.TextField(null=True, blank=True)
    #booking_image = models.ForeignKey(BookingImage, related_name="booking_qc_images", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bhi_updated_by")
    status = models.ForeignKey(master.BookingStatus)
    ops_status = models.ForeignKey(master.BookingOpsStatus)

    def __unicode__(self):
        return "%s" % self.id


class BookingChecklist(CreatedAtAbstractBase):
    booking = models.ForeignKey(Booking, related_name="booking_checklist")
    item = models.ForeignKey(master.ChecklistItem)
    has_issue = models.BooleanField(default=False) # Boolean field (whether issue is there or not)
    is_applicable = models.BooleanField(default=True) # whether item is applicable or not.
    reason_text = models.TextField(null=True, blank=True) # text field if some text/reason for other fields
    media = models.ManyToManyField(Media, related_name="checklist_img")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bchecklist_updated_by")
    status = models.ForeignKey(master.BookingStatus)
    ops_status = models.ForeignKey(master.BookingOpsStatus, null=True, blank=True)
    group_num = models.IntegerField(default=1)
    mismatch = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" % self.id


@receiver(post_save, sender=BookingImage)
def booking_image_post_save(sender, instance, created, **kwargs):
    from core.tasks import upload_to_s3
    if not instance.media.uploaded_to_s3:
        upload_to_s3.delay(instance.booking_id, instance.media_id)


@receiver(post_save, sender=BookingChecklist)
def booking_checklist_post_save(sender, instance, created, **kwargs):
    from core.tasks import upload_to_s3
    for media in instance.media.all():
        if not media.uploaded_to_s3:
            upload_to_s3.delay(instance.booking_id, media.id)


class EntityChangeTracker(models.Model):
    """
        Table to track changes/action to certain entities like eta tracking for booking.
    """
    CONTENT_TYPE_BOOKING = 1
    CONTENT_TYPE_USER = 2

    CONTENT_TYPES = (
        (CONTENT_TYPE_BOOKING, 'Booking'),
        (CONTENT_TYPE_USER, 'User'),
    )

    CHANGE_TYPE_UPDATED = 1
    CHANGE_TYPE_NOT_UPDATED = 2

    CHANGE_TYPES = (
        (CHANGE_TYPE_UPDATED, 'Updated'),
        (CHANGE_TYPE_NOT_UPDATED, 'Not Updated'),
    )
    content_type = models.SmallIntegerField(null=False, blank=False, choices=CONTENT_TYPES)
    content_id = models.IntegerField(null=False, blank=False, db_index=True)
    item_tracked = models.CharField(max_length=64, null=False, blank=False, db_index=True,
                                    help_text="Column name if tracking a column otherwise action")
    change_type = models.SmallIntegerField(null=False, blank=False, choices=CHANGE_TYPES)
    old_value = models.CharField(max_length=1024, null=True, blank=True)
    new_value = models.CharField(max_length=1024, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bc_udpated_by")
    delay_reason = models.ForeignKey(master.DelayReasons, null=True, blank=True, related_name="bc_delay_reason")
    reason_text = models.TextField(null=True, blank=True, default="No Reason")

    def __unicode__(self):
        return "%s - %s" % (self.content_type, self.content_id)

    class Meta:
        verbose_name_plural = 'EntityChangeTracker'


class TeamAlert(CreatedAtAbstractBase):
    """
        Alert raises by Bumper Team members for different processes
    """
    workshop = models.ForeignKey(master.Workshop, null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ta_udpated_by")
    alert_reason = models.ForeignKey(master.TeamAlertReason, related_name="ta_alert_reason")
    reason_text = models.TextField(null=True, blank=True)
    resolved = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s - %s" % (self.updated_by_id, self.alert_reason_id)

    class Meta:
        verbose_name_plural = 'TeamAlert'


class UserVendorCash(CreatedAtAbstractBase):
    ENTITY_BOOKING = "Booking" # Model Name
    ENTITY_SFLEAD = "ScratchFinderLead"
    ENTITY_USER = "BumperUser"

    ENTITY_CHOICES = (
        (ENTITY_BOOKING, ENTITY_BOOKING),
        (ENTITY_SFLEAD, ENTITY_SFLEAD),
        (ENTITY_USER, ENTITY_USER),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_cash",
                             limit_choices_to=Q(groups__name='ScratchFinder'))
    event = models.ForeignKey(incentive.IncentiveEvent)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transferred = models.BooleanField(default=False, db_index=True) # unless transferred, it's just promised.
    settled = models.BooleanField(default=False, db_index=True) # unless settled, it's just transferred.
    cancelled = models.BooleanField(default=False, db_index=True) # after promised, it can be cancelled.
    entity = models.CharField(max_length=64, choices=ENTITY_CHOICES,
                              null=True, blank=True) # if null -> no entity else, entity because of which cash promised.
    entity_id = models.IntegerField(null=True, blank=True)
    promise_info = models.TextField(null=True, blank=True) # Extra information while promising cash
    transfer_info = models.TextField(null=True, blank=True) # Extra information while transferring cash
    settle_info = models.TextField(null=True, blank=True) # PayTM response
    tx_data = models.TextField(null=True, blank=True) # for transfer/settle details

    history = HistoricalRecords()

    def __unicode__(self):
        return "%s" % self.id


class BookingFlag(CreatedAtAbstractBase):
    booking = models.ForeignKey(Booking, related_name="booking_flag")
    flag_type = models.ForeignKey(master.FlagType)
    reason = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("booking", "flag_type")

    def __unicode__(self):
        return "%s" % self.id


class PartDocNote(CreatedAtAbstractBase):
    """
    This table will keep the data for part document for a replace type of panel/part in booking.
    """
    note = models.TextField()
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                                   limit_choices_to=Q(groups__name='OpsUser'))


class BookingPartDoc(CreatedAtAbstractBase):
    """
    This table will keep the data for part document for a replace type of panel/part in booking.
    """
    booking_part = models.ForeignKey(BookingPackagePanel, related_name='booking_part')
    notes = models.ManyToManyField(PartDocNote)
    status = models.ForeignKey(master.PartDocStatus)
    quote_eta = models.DateTimeField(null=True, blank=True)
    # quote_eta_reason - Text as of now - later another dropdown after understanding reasons.
    quote_eta_reason = models.TextField(null=True, blank=True)
    # final_price_cust = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
    #                                        help_text="Inclusive of Tax")
    net_dealer_price = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                                           help_text="Inclusive of Tax")
    mrp = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2,
                              help_text="Inclusive of Tax")
    part_number = models.CharField(max_length=64, null=True, blank=True)
    # TODO: Invoice image - Is this required in current version.

    history = HistoricalRecords()

    def __unicode__(self):
        return "%s" % self.id


class PartQuoteNote(CreatedAtAbstractBase):
    """
    This table will keep the data for part document for a replace type of panel/part in booking.
    """
    note = models.TextField()
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                                   limit_choices_to=Q(groups__name='OpsUser'))


class BookingPartQuote(CreatedAtAbstractBase):
    """
    This table will keep the data for part document for a replace type of panel/part in booking.
    """
    QUOTE_TYPE_OEM = 1
    QUOTE_TYPE_AFTERMARKET = 2
    QUOTE_TYPE_REFURBISHED = 3

    QUOTE_TYPES = (
        (QUOTE_TYPE_OEM, "OEM"),
        (QUOTE_TYPE_AFTERMARKET, "After Market"),
        (QUOTE_TYPE_REFURBISHED, "Refurbished")
    )

    booking_part_doc = models.ForeignKey(BookingPartDoc, related_name='booking_part_doc')
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2,
                                help_text="Inclusive of Tax")
    eta = models.DateTimeField()
    quote_type = models.PositiveSmallIntegerField(choices=QUOTE_TYPES)
    vendor = models.ForeignKey(master.PartVendor)
    notes = models.ManyToManyField(PartQuoteNote)
    selected = models.BooleanField(default=False)

    history = HistoricalRecords()

    def __unicode__(self):
        return "%s" % self.id


class BookingExpectedEOD(CreatedAtAbstractBase):
    """
        For a given day, expected eod can be saved.
        For now not putting in unique together for booking and for_date. Will pick latest update.
    """
    booking = models.ForeignKey(Booking, related_name='booking_expected_eods')
    for_date = models.DateField()
    status = models.ForeignKey(master.BookingStatus, related_name="expected_eod_status")
    ops_status = models.ForeignKey(master.BookingOpsStatus, related_name="expected_epd_ops_status")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="expected_eod_updated_by")

    def __unicode__(self):
        return "%s - %s" % (self.booking_id, self.for_date)