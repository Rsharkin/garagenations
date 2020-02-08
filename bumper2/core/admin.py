from django.contrib import admin
from django.contrib.auth.models import Permission, Group
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
from core.models.incentive import IncentiveEvent
from core.models.users import (
    BumperUser, UserAuthCode, UserDevices, UserCar, PartnerLead, UserInquiry, WorkshopUser, NotificationSubscriber,
    CreditTransaction, UserDetail, UserCredit, Caller
)
from core.models.workshop import WorkshopResources, WorkshopStepsOfWork, WorkshopSla, WorkshopExecutionSteps

from core.models.master import (
    State,
    City,
    CarBrand,
    CarModel,
    Package,
    PackagePrice,
    Item,
    ItemPrice,
    BookingStatus,
    BookingOpsStatus,
    CarPanel,
    CarPanelPrice,
    WorkshopHoliday,
    Workshop,
    Vendor,
    StatusCategory,
    Notifications,
    Hooks,
    CancellationReasons,
    FollowupResult,
    InternalAccounts,
    OpsAlertType,
    DelayReasons,
    CarReturnReasons,
    Source,
    TeamAlertReason,
    ChecklistItem,
    ChecklistCategory,
    DiscountReasons,
    FlagType,
    PartDocStatus,
    PartVendor
)
from core.models.payment import Payment
from core.models.booking import (
    BookingDiscount,
    Booking,
    BookingCoupon,
    BookingInvoice,
    BookingCustFeedback,
    BookingProformaInvoice,
    UserVendorCash,
    EntityChangeTracker,
    BookingExpectedEOD)
from core.models.coupons import Coupon, Campaign
from core.models.message import MessageUser, Messages
from core.models import referral
from utils import capitalize_words
from core.forms import BookingAdminForm


def duplicate_event(modeladmin, request, queryset):
    for object in queryset:
        object.pk = None
        object.save()
duplicate_event.short_description = "Duplicate Selected Records"


def duplicate_record_name_change(modeladmin, request, queryset):
    cnt = 1
    for object in queryset:
        object.pk = None
        object.name += '_' + str(cnt)
        cnt += 1
        object.save()
duplicate_record_name_change.short_description = "Duplicate Selected Records"


class CustomModelAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(CustomModelAdminMixin, self).__init__(model, admin_site)


class BumperUserAdmin(admin.ModelAdmin):
    list_display = ('id','name','email','phone','ops_phone', 'city','date_joined','is_otp_validated','is_email_verified','utm_source',
                    'utm_medium','utm_campaign','source', 'is_active','is_staff')
    search_fields = ['phone', 'email', 'name','ops_phone']
    list_filter = ('is_otp_validated', 'is_staff','groups__name','date_joined', 'city')


class CarPanelAdmin(admin.ModelAdmin):
    list_display = ('id','name','photo','internal','part_type')
    list_filter = ('part_type','internal')
    search_fields = ('name',)

    def save_model(self, request, obj, form, change):
        # Overwritten to send email whenever a car panel is added/changed from admin panel.
        obj.name = capitalize_words(obj.name)
        obj.save()
        add_or_change = 'changed' if change else 'added'
        from core.tasks import send_custom_notification_task
        send_custom_notification_task.delay('OPS_MODEL_ADD_CHANGE_EMAIL',
                                            {'model': 'CarPanel', 'updated_by': request.user.name,
                                             'id':obj.id, 'add_or_change':add_or_change})


class CarPanelPriceAdmin(admin.ModelAdmin):
    list_display = ('id','city','car_panel','car_model','car_type','type_of_work','price','active','editable','internal')
    search_fields = ['car_panel__name', 'car_model__name', 'city__name', 'type_of_work']
    list_filter = ('active', 'car_type','type_of_work','internal','car_model')
    actions = [duplicate_event]

    def save_model(self, request, obj, form, change):
        # Overwritten to send email whenever a car panel is added/changed from admin panel.
        obj.save()
        add_or_change = 'added'
        if change:
            add_or_change = 'changed'
        from core.tasks import send_custom_notification_task
        send_custom_notification_task.delay('OPS_MODEL_ADD_CHANGE_EMAIL',
                                            {'model': 'CarPanel', 'updated_by': request.user.name,
                                             'id':obj.id, 'add_or_change':add_or_change})

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "car_model":
            queryset = CarModel.objects.filter(active=True).order_by('brand__name', 'name', 'start_year')
            kwargs['queryset'] = queryset
        return super(CarPanelPriceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class BookingStatusAdmin(admin.ModelAdmin):
    list_display = ('id','status','status_desc','flow_order_num','is_active')
    list_filter = ('category',)


class BookingOpsStatusAdmin(admin.ModelAdmin):
    list_display = ('id','ops_status','ops_status_desc','flow_order_num', 'show_to_cust')


class UserAuthCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'auth_code', 'expiry_dt', 'system_alert_sent')
    search_fields = ['phone']


class UserCarAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'car_model', 'registration_number', 'purchased_on', 'color', 'active')
    search_fields = ['user']


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'tx_status', 'invoice','amount', 'mode', 'vendor','payment_vendor_id','vendor_status','error_message','tx_data')
    search_fields = ['=invoice__id']


class BookingDiscountAdmin(admin.ModelAdmin):
    list_display = BookingDiscount.get_field_names()
    search_fields = ['booking__id']


class BookingInvoiceAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['booking__id']


class BookingProformaInvoiceAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['booking__id']


class BookingAdmin(SimpleHistoryAdmin):
    form = BookingAdminForm
    list_display = ('id', 'user', 'status', 'ops_status')
    search_fields = ['id']
    exclude = ['followup']


class StatusCategoryAdmin(admin.ModelAdmin):
    list_display = ('id','category','flow_order_num')


class NotificationsAdmin(admin.ModelAdmin):
    # list_display = Notifications.get_field_names()
    list_display = ('id', 'name','type','to','cc','bcc','subject','template','use_file_template',
                    'template_folder_name','send_notice_to','push_level', 'notice_for', 'is_promo')
    list_filter = ('type','use_file_template', 'send_notice_to')
    actions = ['duplicate_notif']
    search_fields = ['name']

    def duplicate_notif(modeladmin, request, queryset):
        for object in queryset:
            object.pk = None
            object.name += '_1'
            object.save()
    duplicate_notif.short_description = "Duplicate Selected Records"


class HooksAdmin(admin.ModelAdmin):
    list_display = ('id', 'action_taken', 'notification')
    list_filter = ['action_taken']


class UserDevicesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'device_id', 'device_type', 'device_info', 'device_os_version', 'app_version',
                    'gcm_device_id', 'apns_device_id', 'is_active', 'is_fcm')
    list_filter = ['device_type', 'is_active', 'is_fcm']
    search_fields = ['user']


class CancellationReasonsAdmin(admin.ModelAdmin):
    list_display = ('id', 'reason', 'reason_owner','order_num', 'active')
    list_filter = ['reason_owner']


class MessageUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_message','sent_to', 'delivered_dt', 'viewed_dt')
    list_filter = ['delivered_dt']
    search_fields = ['user']

    def get_message(self, obj):
        return obj.message.message


class MessagesAdmin(admin.ModelAdmin):
    list_display = ('id','booking','message_type', 'message_send_level', 'direction', 'action', 'notification', 'label', 'viewed_by','sent_by', 'subject', 'message', 'created_at')
    list_filter = ['created_at','message_type', 'message_send_level', 'direction', 'action', 'notification', 'label']
    search_fields = ['booking_id']


class PartnerLeadAdmin(admin.ModelAdmin):
    list_display = PartnerLead.get_field_names()
    list_filter = ['name', 'email', 'mobile']


class CarModelAdmin(admin.ModelAdmin):
    list_display = ('brand','name','start_year','end_year','parent','car_type','popular','active','image_tag')
    list_filter = ['brand','car_type', 'popular','active']
    search_fields = ('brand__name','name','start_year','end_year')
    actions = [duplicate_record_name_change]

    def save_model(self, request, obj, form, change):
        # Overwritten to send email whenever a car panel is added/changed from admin panel.
        obj.save()
        add_or_change = 'created'
        if change:
            add_or_change = 'updated'

        # send email to Ashvin
        from core.models.message import Messages
        from core.tasks import send_async_new_email_service

        notification = Notifications.objects.get(name='OPS_CAR_MODEL_ADD_UPDATE')
        email_body = notification.template % {
            'id': obj.id,
            'change': add_or_change
        }
        send_async_new_email_service.delay(to_list=notification.get_to_list(),
                                           cc_list=notification.get_cc_list(),
                                           subject=notification.subject,
                                           body=email_body,
                                           message_direction=Messages.MESSAGE_DIRECTION_BUMPER_TO_OPS,
                                           analytic_info={
                                               'notification_id': notification.id
                                           })

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "parent":
            queryset = CarModel.objects.filter(parent__isnull=True).order_by('brand__name', 'name')
            kwargs['queryset'] = queryset
        return super(CarModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class UserInquiryAdmin(admin.ModelAdmin):
    list_display = ('user', 'inquiry')
    search_fields = ('user',)


class FollowupResultAdmin(admin.ModelAdmin):
    list_display = ('id','name','active','action_type', 'notification')


class InternalAccountsAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')


class OpsAlertTypeAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['name']


class PackagePriceAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['package__name']
    actions = [duplicate_event]
    list_filter = ['package', 'car_type', 'city']


class PackageAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['name']

    def save_model(self, request, obj, form, change):
        obj.name = capitalize_words(obj.name)
        obj.save()


class BookingCustFeedbackAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'booking_id', 'customer_care','work_quality','value_for_money','any_suggestions')
    search_fields = ['booking_id']


class EntityChangeTrackerAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'content_id', 'item_tracked','change_type')
    search_fields = ['content_id']


class DelayReasonsAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['reason']


class ReturnReasonsAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['reason']


class WorkshopUserAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['user__ops_phone', 'user__name']


class WorkshopAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['name']


class SourceAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['source']


class QualityCheckCategoryAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    # list_display = ('id', 'category', 'active', 'order_num')
    search_fields = ['category']


class QualityCheckAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    # list_display = ('id', 'category', 'quality_check', 'active', 'order_num')
    search_fields = ['quality_check']
    list_filter = ['category']


class BookingQualityChecksAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['booking']


class TeamAlertReasonAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    list_filter = ['reason_type']


class CustomModelAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['=id']


class CouponAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['code']
    actions = ['duplicate_coupon']

    def duplicate_coupon(modeladmin, request, queryset):
        for object in queryset:
            object.pk = None
            object.code += '_1'
            object.save()

    duplicate_coupon.short_description = "Duplicate Selected Coupons"


class UserVendorCashAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ['=entity_id']
    actions = [duplicate_event]


class NotificationSubscriberAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = BumperUser.objects.all().order_by('name')
        return super(NotificationSubscriberAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    list_display = ('id', 'user', 'notification')
    list_filter = ['notification']
    search_fields = ['user']


class ChecklistItemAdmin(CustomModelAdminMixin, admin.ModelAdmin):
    search_fields = ["=id", "name"]
    list_filter = ['category', 'active']


class WorkshopResourcesAdmin(admin.ModelAdmin):
    list_display = ("on_date", "workshop", "denters", "painters", "painter_helpers","polishers", "type_of_record",
                    "updated_by")
    search_fields = ["=id", "on_date"]
    list_filter = ['type_of_record',]


class WorkshopStepsOfWorkAdmin(admin.ModelAdmin):
    list_display = ("type_of_damage", "ops_status", "resources_used", "processing_time_car_level",
                    "processing_time_panel_level")
    search_fields = ["type_of_damage", "resources_used"]
    list_filter = ['type_of_damage', 'ops_status']


class WorkshopExecutionStepsAdmin(admin.ModelAdmin):
    list_display = ("sla", "days_in_workshop", "ops_status", "ops_status_to_consider", "portion")
    search_fields = ["sla", "days_in_workshop", "ops_status"]
    list_filter = ["days_in_workshop", "ops_status"]


class BookingExpectedEODAdmin(admin.ModelAdmin):
    list_display = ('booking', 'for_date', 'status', 'ops_status', 'updated_by', 'created_at')
    search_fields = ['booking__id', 'for_date']
    list_filter = ['for_date',]


admin.site.register(BumperUser, BumperUserAdmin)
admin.site.register(UserAuthCode, UserAuthCodeAdmin)
admin.site.register(UserCar, UserCarAdmin)
admin.site.register(UserDevices, UserDevicesAdmin)
admin.site.register(State)
admin.site.register(City)
admin.site.register(CarBrand)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(PackagePrice, PackagePriceAdmin)
admin.site.register(Item)
admin.site.register(ItemPrice)
admin.site.register(BookingStatus, BookingStatusAdmin)
admin.site.register(BookingOpsStatus, BookingOpsStatusAdmin)
admin.site.register(CarPanel, CarPanelAdmin)
admin.site.register(CarPanelPrice, CarPanelPriceAdmin)
admin.site.register(Workshop, WorkshopAdmin)
admin.site.register(WorkshopHoliday, CustomModelAdmin)
admin.site.register(Vendor)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(BookingDiscount, BookingDiscountAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(StatusCategory, StatusCategoryAdmin)
admin.site.register(Notifications, NotificationsAdmin)
admin.site.register(Hooks, HooksAdmin)
admin.site.register(CancellationReasons, CancellationReasonsAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(BookingCoupon)
admin.site.register(Campaign, CustomModelAdmin)
admin.site.register(MessageUser, MessageUserAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(PartnerLead, PartnerLeadAdmin)
admin.site.register(UserInquiry, UserInquiryAdmin)
admin.site.register(BookingInvoice, BookingInvoiceAdmin)
admin.site.register(BookingProformaInvoice, BookingProformaInvoiceAdmin)
admin.site.register(FollowupResult,FollowupResultAdmin)
admin.site.register(InternalAccounts, InternalAccountsAdmin)
admin.site.register(OpsAlertType, OpsAlertTypeAdmin)
admin.site.register(BookingCustFeedback, BookingCustFeedbackAdmin)
admin.site.register(EntityChangeTracker, EntityChangeTrackerAdmin)
admin.site.register(DelayReasons, DelayReasonsAdmin)
admin.site.register(CarReturnReasons, ReturnReasonsAdmin)
admin.site.register(WorkshopUser, WorkshopUserAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(TeamAlertReason, TeamAlertReasonAdmin)
admin.site.register(ChecklistItem, ChecklistItemAdmin)
admin.site.register(ChecklistCategory, CustomModelAdmin)
admin.site.register(IncentiveEvent, CustomModelAdmin)
admin.site.register(DiscountReasons, CustomModelAdmin)
admin.site.register(UserVendorCash, UserVendorCashAdmin)
admin.site.register(NotificationSubscriber, NotificationSubscriberAdmin)
admin.site.register(referral.ReferralCode, CustomModelAdmin)
admin.site.register(referral.ReferralCampaign, CustomModelAdmin)
admin.site.register(referral.Referral, CustomModelAdmin)
admin.site.register(CreditTransaction, CustomModelAdmin)
admin.site.register(UserDetail, CustomModelAdmin)
admin.site.register(FlagType, CustomModelAdmin)
admin.site.register(UserCredit, CustomModelAdmin)
admin.site.register(WorkshopResources, WorkshopResourcesAdmin)
admin.site.register(PartDocStatus, CustomModelAdmin)
admin.site.register(PartVendor, CustomModelAdmin)
admin.site.register(Permission, CustomModelAdmin)
admin.site.register(WorkshopStepsOfWork, WorkshopStepsOfWorkAdmin)
admin.site.register(WorkshopSla)
admin.site.register(WorkshopExecutionSteps, WorkshopExecutionStepsAdmin)
admin.site.register(BookingExpectedEOD, BookingExpectedEODAdmin)
#admin.site.register(Caller, CustomModelAdmin)
