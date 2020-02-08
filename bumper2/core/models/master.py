import logging

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils.encoding import python_2_unicode_compatible
from multiselectfield import MultiSelectField

from core import constants
from core.models.common import CreatedAtAbstractBase, content_file_name
from core.utils import build_s3_path
from services.s3.storage import S3Storage
from services.settings import BOTO_S3_BUCKET_STATIC

s3 = S3Storage()
s3_static = S3Storage(bucket_name=BOTO_S3_BUCKET_STATIC)
logger = logging.getLogger('__name__')

@python_2_unicode_compatible
class State(CreatedAtAbstractBase):
    name = models.CharField(max_length=64, null=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class City(CreatedAtAbstractBase):
    name = models.CharField(max_length=128, null=False)
    state = models.ForeignKey(State, null=False)
    #is_pms_active = models.BooleanField(default=True)
    is_denting_active = models.BooleanField(default=True)
    is_wash_active = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    service_tax = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base service tax in percentage")
    kk_tax = models.DecimalField(max_digits=10, decimal_places=2, help_text="Krishi Kalyan in percentage")
    sb_tax = models.DecimalField(max_digits=10, decimal_places=2, help_text="Swacch Bharat tax in percentage")
    vat = models.DecimalField(max_digits=10, decimal_places=2, help_text="VAT in percentage")
    cgst = models.DecimalField(max_digits=10, decimal_places=2, default=9,
                               help_text="CGST - Center GST in percentage")
    sgst = models.DecimalField(max_digits=10, decimal_places=2, default=9,
                               help_text="SGST - State GST in percentage")
    igst = models.DecimalField(max_digits=10, decimal_places=2, default=18,
                               help_text="IGST - Inter state GST in percentage")
    # Need to figure out a way to handle multiple states within regions for GST
    state_code = models.CharField(max_length=10, null=False, help_text="This is for GST")
    state_name = models.CharField(max_length=128, null=False, help_text="This is for GST")
    gstin = models.CharField(max_length=20, null=False, help_text="GST Number for this state")
    invoice_address = models.TextField(null=True, blank=True, help_text="This will be the address on invoice")

    class Meta:
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class CarBrand(CreatedAtAbstractBase):
    name = models.CharField(max_length=128)
    logo = models.FileField(null=True, upload_to=content_file_name, storage=s3, help_text="Logo of the brand")
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.name

    def __str__(self):
        return "%s" % self.name

    def image_tag(self):
        if self.logo:
            return '<img src="%s" width="50px" height="50px"/>' % build_s3_path(self.logo.name)
        else:
            return 'No Image'
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


@python_2_unicode_compatible
class CarColor(CreatedAtAbstractBase):
    color_name = models.CharField(max_length=128, unique=True)
    color_code = models.CharField(max_length=32, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.color_name

    def __str__(self):
        return self.color_name


@python_2_unicode_compatible
class CarModelVariant(CreatedAtAbstractBase):
    # car_model = models.ForeignKey(CarModel, related_name="carvariant")
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class CarModel(CreatedAtAbstractBase):
    CAR_HATCHBACK = 1
    CAR_SEDAN = 2
    CAR_SUV = 3
    CAR_LUXURY = 4
    CAR_HATCHBACK1 = 5
    CAR_HATCHBACK2 = 6
    CAR_HATCHBACK3 = 7
    CAR_SEDAN1 = 8
    CAR_SEDAN2 = 9
    CAR_SEDAN3 = 10
    CAR_SUV1 = 11
    CAR_SUV2 = 12
    CAR_SUV3 = 13

    CAR_TYPES = (
        (CAR_HATCHBACK,'Hatchback'),
        (CAR_SEDAN,'Sedan'),
        (CAR_SUV,'SUV'),
        (CAR_LUXURY,'Luxury'),
        (CAR_HATCHBACK1,'Hatchback1'),
        (CAR_HATCHBACK2,'Hatchback2'),
        (CAR_HATCHBACK3,'Hatchback3'),
        (CAR_SEDAN1, 'Sedan1'),
        (CAR_SEDAN2, 'Sedan2'),
        (CAR_SEDAN3, 'Sedan3'),
        (CAR_SUV1, 'SUV1'),
        (CAR_SUV2, 'SUV2'),
        (CAR_SUV3, 'SUV3'),
    )

    brand = models.ForeignKey(CarBrand,related_name='carmodel')
    name = models.CharField(max_length=128, db_index=True)
    start_year = models.IntegerField(choices=constants.YEAR_CHOICES, null=True, blank=True)
    end_year = models.IntegerField(choices=constants.YEAR_CHOICES, null=True, blank=True)
    photo = models.FileField(null=True,blank=True,upload_to=content_file_name, storage=s3,
                             help_text="Photo of the car")
    car_type = models.SmallIntegerField(choices=CAR_TYPES, default=CAR_HATCHBACK1, db_index=True)
    popular = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    show_savings = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True)
    colors = models.ManyToManyField(CarColor, blank=True)
    variants = models.ManyToManyField(CarModelVariant, blank=True)

    class Meta:
        unique_together = ("brand", "name", "start_year", "end_year")
        ordering = ['name']

    def __unicode__(self):
        return "%s - %s (%s - %s)" % (self.brand, self.name, self.start_year, self.end_year)

    def __str__(self):
        return "%s - %s (%s - %s)" % (self.brand, self.name, self.start_year, self.end_year)

    def get_desc(self):
        return "%s - %s" % (self.brand, self.name)

    def image_tag(self):
        if self.photo:
            return '<img src="%s" width="75px" height="50px"/>' % build_s3_path(self.photo.name)
        else:
            return 'No Image'
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    @property
    def photo_url(self):
        return build_s3_path(self.photo.name)

    @staticmethod
    def get_car_models_by_sync_time(last_sync_time=None):
        if last_sync_time:
            cbs = CarModel.objects.filter(updated_at__gt=last_sync_time).order_by('name')
        else:
            cbs = CarModel.objects.filter(active=True).order_by('name')

        item_list = []
        for item in cbs:
            model_dict = model_to_dict(item)
            model_dict['updated_at'] = str(item.updated_at)
            model_dict['created_at'] = str(item.created_at)
            if item.photo:
                model_dict['photo'] = build_s3_path(str(item.photo.name))
            else:
                model_dict['photo'] = None
            item_list.append(model_dict)

        return item_list

    def get_car_model_by_year(self, year):
        # This method will return the car model which matches with given year or else the parent model
        if self.parent:
            parent = self.parent
        else:
            parent = self
        children = CarModel.objects.filter(models.Q(parent=parent) &
                                           (models.Q(start_year__lte=year) | models.Q(start_year__isnull=True)) &
                                           (models.Q(end_year__gte=year) | models.Q(end_year__isnull=True))
                                           ).order_by('start_year', 'end_year')
        output = None
        for child in children:
            if child.start_year <= year <= child.end_year:
                output = child
            elif child.start_year <= year and not child.end_year:
                output = child
            elif child.start_year is None and child.end_year >= year:
                output = child
        if not output:
            output = parent
        return output


class StatusCategory(CreatedAtAbstractBase):
    id = models.IntegerField(primary_key=True)
    category = models.CharField(max_length=128,unique=True)
    flow_order_num = models.SmallIntegerField(null=False, default=1)

    class Meta:
        verbose_name_plural = 'Status Categories'
        ordering = ['flow_order_num']

    def __str__(self):
        return "%s" % self.category

    def __unicode__(self):
        return "%s" % self.category


class BookingStatus(CreatedAtAbstractBase):
    id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=128,unique=True)
    status_desc = models.CharField(max_length=256)
    flow_order_num = models.SmallIntegerField(null=False, default=1)
    category = models.ForeignKey(StatusCategory,null=True,blank=True)
    is_checkpoint = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Booking Statuses'
        ordering = ['flow_order_num']

    def __str__(self):
        return "%s" % self.status

    def __unicode__(self):
        return "%s" % self.status


class BookingOpsStatus(CreatedAtAbstractBase):
    id = models.IntegerField(primary_key=True)
    #status = models.ForeignKey(BookingStatus)
    ops_status = models.CharField(max_length=128)
    ops_status_desc = models.CharField(max_length=256)
    flow_order_num = models.SmallIntegerField(default=1)
    show_to_cust = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Booking Ops Statuses'
        ordering = ['flow_order_num']

    def __str__(self):
        return "%s - %s" % (self.flow_order_num, self.ops_status)

    def __unicode__(self):
        return "%s - %s" % (self.flow_order_num, self.ops_status)


class Item(CreatedAtAbstractBase):
    name = models.CharField(max_length=128)
    desc = models.CharField(max_length=512)
    #city = models.ForeignKey(City)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.name


class ItemPrice(CreatedAtAbstractBase):
    item = models.ForeignKey(Item)
    price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    car_type = models.SmallIntegerField(choices=CarModel.CAR_TYPES)

    def __unicode__(self):
        car_type_dict = dict(CarModel.CAR_TYPES)
        return "%s-Rs %s-%s" % (self.item.name, self.price, car_type_dict.get(self.car_type))


class Package(CreatedAtAbstractBase):
    CATEGORY_VAS = 1
    CATEGORY_DENT = 2
    CATEGORY_FULL_BODY = 3
    CATEGORY_ADV_PAYMENT_TO = 4
    CATEGORY_ADV_PAYMENT_FROM = 5

    CATEGORY_TYPES = (
        (CATEGORY_VAS, "VAS"),
        (CATEGORY_DENT, "Denting"),
        (CATEGORY_FULL_BODY, "Full Body Paint"),
        (CATEGORY_ADV_PAYMENT_TO, "Advance Payment To"),
        (CATEGORY_ADV_PAYMENT_FROM, "Advance Payment From")
    )

    PICKUP_BUMPER = 1
    PICKUP_WORKSHOP = 2
    PICKUP_SELF = 3

    PICKUP_TYPES = (
        (PICKUP_BUMPER, "Bumper"),
        (PICKUP_WORKSHOP, "Workshop"),
        (PICKUP_SELF, "Self"),
    )

    name = models.CharField(max_length=128)
    desc = models.CharField(max_length=512)
    long_desc = models.CharField(max_length=2048, null=True, blank=True)
    category = models.PositiveSmallIntegerField(choices=CATEGORY_TYPES)
    pickup_type = models.PositiveSmallIntegerField(choices=PICKUP_TYPES)
    is_doorstep = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    items = models.ManyToManyField(Item)
    photo = models.FileField(null=True, upload_to=content_file_name, storage=s3, help_text="Photo of Package")
    sort_order = models.PositiveIntegerField(null=True, blank=True)
    popular = models.BooleanField(default=False)
    internal = models.BooleanField(default=True, help_text="These packages price can be editable from backend.")
    desc_url = models.CharField(max_length=256,null=True,blank=True)
    website_desc_url = models.CharField(max_length=256,null=True,blank=True)

    def __unicode__(self):
        return "{name} - {doorstep}".format(name=self.name, doorstep="Doorstep" if self.is_doorstep else "Not Doorstep")

    @property
    def photo_url(self):
        return build_s3_path(self.photo.name)

    def image_tag(self):
        if self.photo:
            return '<img src="%s" width="75px" height="50px"/>' % build_s3_path(self.photo.name)
        else:
            return 'No Image'
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class PackagePrice(CreatedAtAbstractBase):
    package = models.ForeignKey(Package)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    part_price = models.DecimalField(max_digits=10,decimal_places=2, help_text="Inclusive of Tax")
    material_price = models.DecimalField(max_digits=10,decimal_places=2, help_text="Inclusive of Tax")
    labour_price = models.DecimalField(max_digits=10,decimal_places=2, help_text="Inclusive of Tax")
    car_type = models.SmallIntegerField(choices=CarModel.CAR_TYPES)
    dealer_part_price = models.DecimalField(default=0, max_digits=10, decimal_places=2,
                                            help_text="Inclusive of Tax")
    dealer_material_price = models.DecimalField(default=0, max_digits=10, decimal_places=2,
                                                help_text="Inclusive of Tax")
    dealer_labour_price = models.DecimalField(default=0, max_digits=10, decimal_places=2,
                                              help_text="Inclusive of Tax")
    show_savings = models.BooleanField(default=False)
    city = models.ForeignKey(City)

    def __unicode__(self):
        car_type_dict = dict(CarModel.CAR_TYPES)
        return "%s-Rs %s-%s" % (self.package.name, self.part_price, car_type_dict.get(self.car_type))

    def __str__(self):
        car_type_dict = dict(CarModel.CAR_TYPES)
        return "%s-Rs %s-%s" % (self.package.name, self.part_price, car_type_dict.get(self.car_type))


class CarPanel(CreatedAtAbstractBase):
    PART_PANEL = 1
    PART_SPARE_PART = 2

    PART_TYPES = (
        (PART_PANEL, 'Panel'),
        (PART_SPARE_PART, 'Spare Part'),
    )

    name = models.CharField(max_length=128)
    photo = models.FileField(upload_to=content_file_name, storage=s3, help_text="Panel of the car shown on list page")
    # photo_thumbnail = ImageSpecField(source='photo', cachefile_storage=s3,
    #                                   processors=[ResizeToFill(100, 50)],
    #                                   format='JPEG',
    #                                   options={'quality': 70})
    big_photo = models.FileField(upload_to=content_file_name, storage=s3, help_text="Panel of the car shown on detail page")
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(null=True, blank=True)
    internal = models.BooleanField(default=True, help_text="These panels price can be editable from backend.",
                                   db_index=True)
    part_type = models.PositiveSmallIntegerField(choices=PART_TYPES, default=PART_PANEL, db_index=True)

    def __unicode__(self):
        return "%s - %s" % (self.name,self.part_type)

    @property
    def photo_url(self):
        return build_s3_path(self.photo.name)

    @property
    def big_photo_url(self):
        return build_s3_path(self.photo.name)


class CancellationReasons(CreatedAtAbstractBase):
    REASON_OWNER_CUSTOMER = 1
    REASON_OWNER_OPS = 2
    REASON_OWNER_SYSTEM = 3

    REASON_OWNERS = (
        (REASON_OWNER_CUSTOMER,'Customer'),
        (REASON_OWNER_OPS,'Ops'),
        (REASON_OWNER_SYSTEM,'System')
    )

    reason = models.CharField(max_length=64)
    reason_owner = models.PositiveSmallIntegerField(choices=REASON_OWNERS)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % (self.reason)


class CarPanelPrice(CreatedAtAbstractBase):
    """
    This is the repair price for each panel per car type per city.
    """
    TYPE_OF_WORK_SCRATCH = 1
    TYPE_OF_WORK_DENT = 2
    TYPE_OF_WORK_REPLACE = 3
    TYPE_OF_WORK_PAINT_ONLY = 4
    TYPE_OF_WORK_CRUMPLED_PANEL = 5
    TYPE_OF_WORK_RUSTED_PANEL = 6
    TYPE_OF_WORK_TEAR = 7
    TYPE_OF_WORK_CLEANING = 8
    TYPE_OF_WORK_REPLACE_FBB = 9
    TYPE_OF_WORK_REPAIR = 10  # for spare parts

    TYPE_OF_WORKS = (
        (TYPE_OF_WORK_SCRATCH, "Remove Scratches"),
        (TYPE_OF_WORK_DENT, "Remove Dents and Scratches"),
        (TYPE_OF_WORK_REPLACE, "Replace"),
        (TYPE_OF_WORK_PAINT_ONLY, "Paint Only"),
        (TYPE_OF_WORK_CRUMPLED_PANEL, "Crumpled panel"),
        (TYPE_OF_WORK_RUSTED_PANEL, "Fix Rusted Area"),
        (TYPE_OF_WORK_TEAR, "Tear"),
        (TYPE_OF_WORK_CLEANING, "Cleaning"),
        (TYPE_OF_WORK_REPLACE_FBB, "Replace"),
        (TYPE_OF_WORK_REPAIR, "Repair Part"),
    )

    TYPE_OF_WORK_ORDERING = [2, 1, 3, 4, 5, 6, 7, 8, 9, 10]

    car_panel = models.ForeignKey(CarPanel, related_name='panel_price')
    car_type = models.PositiveSmallIntegerField(choices=CarModel.CAR_TYPES, null=True, blank=True,
                                                db_index=True)
    car_model = models.ForeignKey(CarModel,null=True,blank=True)
    city = models.ForeignKey(City)
    type_of_work = models.PositiveSmallIntegerField(choices=TYPE_OF_WORKS, db_index=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    part_price = models.DecimalField(max_digits=10,decimal_places=2, help_text="Inclusive of Tax",null=True,blank=True)
    material_price = models.DecimalField(max_digits=10,decimal_places=2, help_text="Inclusive of Tax",
                                         null=True, blank=True)
    labour_price = models.DecimalField(max_digits=10,decimal_places=2, help_text="Inclusive of Tax",
                                       null=True, blank=True)
    active = models.BooleanField(default=True)
    editable = models.BooleanField(default=False, help_text="This panel price can be editable from backend.")
    internal = models.BooleanField(default=False, help_text="This panel price can only be seen on backend.",
                                   db_index=True)
    dealer_part_price = models.DecimalField(default=0, max_digits=10,decimal_places=2,
                                            help_text="Inclusive of Tax")
    dealer_material_price = models.DecimalField(default=0, max_digits=10, decimal_places=2,
                                            help_text="Inclusive of Tax")
    dealer_labour_price = models.DecimalField(default=0, max_digits=10, decimal_places=2,
                                            help_text="Inclusive of Tax")
    show_savings = models.BooleanField(default=False)
    photo = models.FileField(upload_to=content_file_name, storage=s3, help_text="Panel of the car shown on list page",
                             null=True, blank=True)
    big_photo = models.FileField(upload_to=content_file_name, storage=s3,
                                 help_text="Panel of the car shown on detail page",
                                 null=True, blank=True)

    def __unicode__(self):
        #car_type_dict = dict(CarModel.CAR_TYPES)
        return "%s" % self.id


class Vendor(CreatedAtAbstractBase):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.name


class Workshop(CreatedAtAbstractBase):
    DAY_CHOICES = (
        (0,'Monday'),
        (1,'Tuesday'),
        (2,'Wednesday'),
        (3,'Thursday'),
        (4,'Friday'),
        (5,'Saturday'),
        (6,'Sunday')
    )

    vendor = models.ForeignKey(Vendor)
    name = models.CharField(max_length=255,null=True)
    short_address = models.CharField(null=True,max_length=128)
    address = models.CharField(max_length=1024)
    latitude = models.DecimalField(max_digits=10,decimal_places=7)
    longitude = models.DecimalField(max_digits=10,decimal_places=7)
    logo = models.FileField(upload_to=content_file_name, storage=s3, help_text="Logo of Workshop",null=True, blank=True)
    open_at = models.TimeField()
    close_at = models.TimeField()
    off_days = MultiSelectField(choices=DAY_CHOICES,null=True,blank=True)
    active = models.BooleanField(default=True)
    city = models.ForeignKey(City)
    is_doorstep = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.name

    def __unicode__(self):
        return "%s" % self.name

    def image_tag(self):
        if self.logo:
            return '<img src="%s" width="50px" height="50px"/>' % build_s3_path(self.logo.name)
        else:
            return 'No Image'
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class WorkshopHoliday(CreatedAtAbstractBase):
    workshop = models.ForeignKey(Workshop)
    holiday_date = models.DateField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s" % self.id


class Notifications(CreatedAtAbstractBase):
    """
        Notification Templates.
    """
    NOTIFICATION_TYPE_EMAIL = 1
    NOTIFICATION_TYPE_SMS = 2
    NOTIFICATION_TYPE_PUSH = 3

    NOTIFICATION_TYPES = (
        (NOTIFICATION_TYPE_EMAIL, 'Email'),
        (NOTIFICATION_TYPE_SMS, 'SMS'),
        (NOTIFICATION_TYPE_PUSH, 'Push'),
    )

    LABEL_STATUS = 1
    LABEL_FEEDBACK = 2
    LABEL_UPDATE = 3
    LABEL_OFFER = 4
    LABEL_REFERRAL = 5
    LABEL_RATE_US = 6
    LABEL_FILL_PROFILE = 7
    LABEL_FILL_CAR_INFO = 8
    LABEL_EOD = 9
    LABEL_REQUEST_LOCATION = 10
    LABEL_CANCEL_RETARGET = 11

    LABEL_TYPES = (
        (LABEL_STATUS, 'Status'),
        (LABEL_FEEDBACK, 'Feedback'),
        (LABEL_UPDATE, 'Update'),
        (LABEL_OFFER, 'Offer'),
        (LABEL_REFERRAL, 'Referral'),
        (LABEL_RATE_US, 'RateUs'),
        (LABEL_FILL_PROFILE, 'FillProfile'),
        (LABEL_FILL_CAR_INFO, 'FillCarInfo'),
        (LABEL_EOD, 'EOD'),
        (LABEL_REQUEST_LOCATION, 'Req. Loc.'),
        (LABEL_CANCEL_RETARGET, 'CancelRetarget'),
    )

    NOTICE_FOR_FLOW = 'flow'
    NOTICE_FOR_EOD = 'eod'

    NOTICE_FOR_TYPES = (
        (NOTICE_FOR_FLOW, 'Flow'),
        (NOTICE_FOR_EOD, 'EOD'),
    )
    SEND_NOTICE_TO_CUSTOMER = 1
    SEND_NOTICE_TO_OPS = 2
    SEND_NOTICE_TO_PICKUP_DRIVER = 3
    SEND_NOTICE_TO_DROP_DRIVER = 4
    SEND_NOTICE_TO_WORKSHOP_EXECUTIVE = 5
    SEND_NOTICE_TO_CUSTOM = 6

    NOTICE_SEND_TO_TYPES = (
        (SEND_NOTICE_TO_CUSTOMER, 'Customer'),
        (SEND_NOTICE_TO_OPS, 'Ops'),
        (SEND_NOTICE_TO_PICKUP_DRIVER, 'Pickup Driver'),
        (SEND_NOTICE_TO_DROP_DRIVER, 'Drop Driver'),
        (SEND_NOTICE_TO_WORKSHOP_EXECUTIVE, 'Workshop Executive'),
        (SEND_NOTICE_TO_CUSTOM, 'Custom Number/Email'),
    )

    name = models.CharField(max_length=64, null=False, help_text="Do not change this, "
                                                                              "this is used in code. Eg. TempName1")
    type = models.SmallIntegerField(choices=NOTIFICATION_TYPES, null=False, blank=False)
    priority = models.SmallIntegerField(default=1, help_text="Do not change this, this is for the scheduler.")
    to = models.CharField(max_length=64, null=True, blank=True,
                          help_text="Emails comma separated, For SMS this will be phone number without +91.",)
    cc = models.CharField(max_length=512, null=True, blank=True, help_text="Comma separated values expected.")
    bcc = models.CharField(max_length=512, null=True, blank=True, help_text="Comma separated values expected.")
    subject = models.CharField(max_length=128, null=True, blank=True)
    template = models.TextField(null=False)
    is_promo = models.BooleanField(default=False, help_text="You want to send a promotional SMS?")
    use_file_template = models.BooleanField(default=False, help_text="Using file template as content?")
    template_folder_name = models.CharField(max_length=64, null=True, blank=True,help_text="If use_template is true "
                                                                                           "then name of the folder of "
                                                                                           "mailer template is "
                                                                                           "required.")
    #only_for_user = models.BooleanField(default=False, help_text="In this case to field will not be used.")
    push_level = models.SmallIntegerField(choices=LABEL_TYPES, null=True, blank=True, default=LABEL_STATUS)
    notice_for = models.CharField(max_length=4, null=False, blank=False, default=NOTICE_FOR_FLOW,
                                  choices=NOTICE_FOR_TYPES)

    send_notice_to = models.SmallIntegerField(null=False, blank=False, default=SEND_NOTICE_TO_OPS,
                                              choices=NOTICE_SEND_TO_TYPES)

    class Meta:
        verbose_name_plural = 'Notifications'
        unique_together = ('name', 'type')

    def __unicode__(self):
        return "%s - %s" % (self.id, self.name)

    # @staticmethod
    # def get_field_names():
    #     fnames = Notifications._meta.get_all_field_names()
    #     fnames.remove('hook_notifications')
    #     return fnames

    def get_cc_list(self):
        cc_list_str = self.cc
        cc_list = []
        cc_aar = str(str(cc_list_str).strip()).split(',')
        for item in cc_aar:
            cleaned_item = item.strip()
            if cleaned_item:
                cc_list.append(cleaned_item)

        return cc_list

    def get_to_list(self):
        to_list_str = self.to
        to_list = []
        to_aar = str(to_list_str.strip()).split(',')
        for item in to_aar:
            cleaned_item = item.strip()
            if cleaned_item:
                to_list.append(cleaned_item)

        return to_list


class Hooks(CreatedAtAbstractBase):
    class Meta:
        verbose_name_plural = 'Hooks'

    def __unicode__(self):
        return "%s" % self.id

    action_taken = models.IntegerField(null=False, blank=False)
    notification = models.ForeignKey(Notifications, null=False, related_name="hook_notifications")


class FollowupResult(CreatedAtAbstractBase):
    FOLLOWUP_ACTION_FOLLOWUP = 1
    FOLLOWUP_ACTION_ASSIGNED = 2

    FOLLOWUP_ACTIONS = (
        (FOLLOWUP_ACTION_FOLLOWUP, "Followup"),
        (FOLLOWUP_ACTION_ASSIGNED, "Assigned")
    )

    FOLLOWUP_CUSTOMER = 1
    FOLLOWUP_INTERNAL = 2

    FOLLOWUP_FOR_TYPES = (
        (FOLLOWUP_CUSTOMER, "Customer Voice"),
        (FOLLOWUP_INTERNAL, "Internal Notes")
    )

    def __unicode__(self):
        return "%s" % self.name

    name = models.CharField(max_length=64, null=False,blank=False)
    active = models.BooleanField(default=True)
    action_type = models.PositiveSmallIntegerField(choices=FOLLOWUP_ACTIONS)
    notification = models.ForeignKey(Notifications, null=True, blank=True)
    result_type = models.PositiveSmallIntegerField(choices=FOLLOWUP_FOR_TYPES, default=FOLLOWUP_CUSTOMER)


class InternalAccounts(CreatedAtAbstractBase):
    """
        This model will be used
    """
    def __unicode__(self):
        return "%s" % self.name

    name = models.CharField(max_length=64, null=False,blank=False)
    phone = models.CharField(max_length=10, null=False, blank=False, unique=True)


class OpsAlertType(CreatedAtAbstractBase):
    """
        Master table for Ops Alerts Trigger.
    """
    def __unicode__(self):
        return "%s" % self.name

    #id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1024)
    time_diff = models.IntegerField(help_text="in minutes")
    time_field = models.CharField(max_length=128, null=True, blank=True,
                                  help_text="this is the field in booking table "
                                            "with which the time diff will be calculated. "
                                            "If this is empty, then current time will be used.")
    time_field_range = models.BooleanField(null=False, blank=False, default=False,
                                  help_text="this tells whether the time_field is range.")
    filter_conditions = models.CharField(max_length=1024, null=False, blank=False,
                                         help_text="Static Django Query Conditions for filtering the bookings")
    exclude_conditions = models.CharField(max_length=1024, null=True, blank=True,
                                          help_text="Django Query Conditions for excluding the bookings")
    notification = models.ForeignKey(Notifications)


class InquiryCancellationReasons(CreatedAtAbstractBase):
    REASON_OWNER_CUSTOMER = 1
    REASON_OWNER_OPS = 2

    REASON_OWNERS = (
        (REASON_OWNER_CUSTOMER,'Customer'),
        (REASON_OWNER_OPS,'Ops')
    )

    reason = models.CharField(max_length=64)
    reason_owner = models.PositiveSmallIntegerField(choices=REASON_OWNERS)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % (self.reason)


class DelayReasons(CreatedAtAbstractBase):
    DELAY_REASON_CUSTOMER = 1 # when customer eta changed
    DELAY_REASON_WORKSHOP = 2 # when workshop eta changed

    DELAY_REASON_TYPES = (
        (DELAY_REASON_CUSTOMER, "Customer ETA changed"),
        (DELAY_REASON_WORKSHOP, "Workshop ETA changed")
    )
    reason = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    reason_type = models.PositiveSmallIntegerField(choices=DELAY_REASON_TYPES)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % (self.reason)

    class Meta:
        verbose_name_plural = 'DelayReasons'


class CarReturnReasons(CreatedAtAbstractBase):
    reason = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % (self.reason)


class DiscountReasons(CreatedAtAbstractBase):
    reason = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % (self.reason)


class Source(CreatedAtAbstractBase):
    # Booking / User / UserInquiry source
    source = models.CharField(max_length=16, primary_key=True)
    source_desc = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % (self.source)


class QualityCheckCategory(CreatedAtAbstractBase):
    """
        Categories for QC and there list.
    """
    category = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % self.category

    class Meta:
        verbose_name_plural = 'QualityCheckCategories'


class QualityCheck(CreatedAtAbstractBase):
    """
        Model for master list of quality checks.
    """
    quality_check = models.CharField(max_length=512)
    category = models.ForeignKey(QualityCheckCategory, null=False, related_name="quality_checks_list")
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % self.id

    class Meta:
        verbose_name_plural = 'QualityChecks'


class TeamAlertReason(CreatedAtAbstractBase):
    ALERT_REASON_WORKSHOP = 1  # Raised by workshop team
    ALERT_REASON_DRIVER = 2  # Raised by Crew member

    ALERT_REASON_TYPES = (
        (ALERT_REASON_WORKSHOP, "Raised by workshop team"),
        (ALERT_REASON_DRIVER, "Raised by Crew team")
    )
    reason = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    reason_type = models.PositiveSmallIntegerField(choices=ALERT_REASON_TYPES)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % (self.reason)


class HandoverItem(CreatedAtAbstractBase):
    """
        Model for master list of handover items
    """
    name = models.CharField(max_length=512)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % self.id


class ChecklistCategory(CreatedAtAbstractBase):
    """
        Categories for checklist
    """
    category = models.CharField(max_length=64)
    is_qc = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % self.category

    class Meta:
        verbose_name_plural = 'Checklist Categories'


class DeliveryReasons(CreatedAtAbstractBase):
    reason = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % self.reason


class ChecklistItem(CreatedAtAbstractBase):
    """
        Model for creating different types of checklists.
    """
    ITEM_TYPE_BOOLEAN = 1
    ITEM_TYPE_IMAGE = 2
    ITEM_TYPE_NUMBER = 3

    ITEM_TYPES = (
        (ITEM_TYPE_BOOLEAN, "Boolean"),
        (ITEM_TYPE_IMAGE, "Image"),
        (ITEM_TYPE_NUMBER, "Number"),
    )
    name = models.CharField(max_length=128)
    category = models.ForeignKey(ChecklistCategory)
    item_type = models.PositiveSmallIntegerField(choices=ITEM_TYPES, default=ITEM_TYPE_BOOLEAN)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()
    photo_mandatory = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" % self.name


class FlagType(CreatedAtAbstractBase):
    """
        Model for flag types for booking
    """
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % self.name


class PartDocStatus(CreatedAtAbstractBase):
    """
        Model for part document statuses
    """
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    order_num = models.IntegerField()

    def __unicode__(self):
        return "%s" % self.name


class PartVendor(CreatedAtAbstractBase):
    """
        Model for part vendors
    """
    name = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    city = models.ForeignKey(City)
    address = models.TextField()

    def __unicode__(self):
        return "%s" % self.name


@receiver(pre_save, sender=CarPanelPrice)
def pre_save_handler(sender, instance, *args, **kwargs):
    if not instance.car_model and not instance.car_type:
        raise Exception('One of Car type/model is mandatory')


@receiver(post_save, sender=CarModel)
def post_save_handler(sender, instance, created, *args, **kwargs):
    if not instance.photo:
        instance.photo = "dfcd0bd1-371f-4ead-a4a6-86f729302f81.png"
        instance.save()
