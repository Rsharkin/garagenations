from django.conf.urls import url, include
from rest_framework import routers

import api.api_views.bookingViews
from api.api_views import masterViews, userViews, bookingViews, reportViews, notifViews, workshopViews, webhookViews

router = routers.DefaultRouter()
router.register(r'city', masterViews.CityViewSet)
router.register(r'state', masterViews.StateViewSet)
router.register(r'user', userViews.UserViewSet)
router.register(r'brand', masterViews.CarBrandViewSet)
router.register(r'model', masterViews.CarModelViewSet)
router.register(r'panel', masterViews.CarPanelViewSet)
router.register(r'usercar', userViews.UserCarViewSet)
router.register(r'package', masterViews.PackagePriceViewSet)
router.register(r'booking', bookingViews.BookingViewSet,base_name='booking')
router.register(r'booking-package', bookingViews.BookingPackageViewSet)
router.register(r'booking-panel', bookingViews.BookingPackagePanelViewSet)
router.register(r'user-address', userViews.UserAddressViewSet)
router.register(r'booking-address', bookingViews.BookingAddressViewSet)
router.register(r'booking-bill', bookingViews.BookingBillViewSet,base_name='bill')
router.register(r'booking-status', bookingViews.BookingStatusViewSet)
router.register(r'payment', bookingViews.PaymentViewSet)
router.register(r'driver-booking', bookingViews.DriverBookingViewSet)
router.register(r'booking-jobcard', bookingViews.BookingImageViewSet)
router.register(r'booking-discount', bookingViews.BookingDiscountViewSet)
router.register(r'booking-coupon', bookingViews.BookingCouponViewSet)
router.register(r'report', reportViews.ReportViewSet, 'report')
router.register(r'notify-users', reportViews.NotificationViewSet, 'notice')
router.register(r'partner-lead', userViews.PartnerLeadViewSet)
router.register(r'user-inquiry', userViews.UserInquiryViewSet)
router.register(r'booking-feedback', bookingViews.BookingFeedbackViewSet)
router.register(r'booking-cust-feedback', bookingViews.BookingCustFeedbackViewSet)
router.register(r'marketing-campaign', userViews.MarketingCampaignSet,base_name='marketing')
router.register(r'entity-change', bookingViews.EntityChangeTrackerViewSet)
router.register(r'booking-proforma-invoice', bookingViews.BookingProformaInvoiceViewSet)
router.register(r'booking-rework-package', bookingViews.BookingReworkPackageViewSet)
router.register(r'booking-rework-panel', bookingViews.BookingReworkPackagePanelViewSet)
router.register(r'workshop-booking', bookingViews.WorkshopBookingViewSet)
router.register(r'workshop-user', userViews.WorkshopUserViewSet)
router.register(r'driver-location', userViews.DriverLocationViewSet)
router.register(r'user-attendance', userViews.UserAttendanceViewSet)
router.register(r'quality-checks', masterViews.QualityCheckViewSet)
router.register(r'booking-quality-checks', bookingViews.BookingQualityCheckViewSet)
router.register(r'raise-alert', bookingViews.TeamAlertViewSet)
router.register(r'booking-handover', bookingViews.BookingHandoverViewSet)
router.register(r'handover-item', masterViews.HandoverItemViewSet)
router.register(r'checklist', masterViews.ChecklistItemViewSet)
router.register(r'booking-checklist', bookingViews.BookingChecklistViewSet)
router.register(r'sflead', userViews.ScratchFinderLeadViewSet) # scratch finder leads
router.register(r'booking-flag', bookingViews.BookingFlagViewSet)
router.register(r'referral-code', userViews.ReferralCodeViewSet)
router.register(r'credit-history', userViews.CreditTransactionViewSet)
router.register(r'workshop-resources', workshopViews.WorkshopResourcesViewSet)
router.register(r'part-doc', bookingViews.BookingPartDocViewSet)
router.register(r'part-quote', bookingViews.BookingPartQuoteViewSet)
router.register(r'part-vendor', masterViews.PartVendorViewSet)
router.register(r'expected-eod', bookingViews.BookingExpectedEODViewSet)
router.register(r'panel-history', bookingViews.BPPHistoryViewSet)
router.register(r'webhook', webhookViews.FacebookLeadViewSet, base_name='webhook')

routerv2 = routers.DefaultRouter()
routerv2.register(r'booking', bookingViews.BookingViewSet, base_name='bookingv2')
routerv2.register(r'booking-bill', bookingViews.BookingBillViewSet, base_name='booking_billv2')


class BulkUpdateRouter(routers.DefaultRouter):
    routes = routers.SimpleRouter.routes
    routes[0] = routers.Route(
        url=r'^{prefix}{trailing_slash}$',
        mapping={
            'get': 'list',
            'post': 'create',
            'put': 'bulk_update',
            'patch': 'partial_bulk_update'
        },
        name='{basename}-list',
        initkwargs={'suffix': 'List'}
    )

bulk_router = BulkUpdateRouter()
bulk_router.register(r'notification', notifViews.MessageViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls, namespace='')),
    url(r'^v2/', include(routerv2.urls, namespace='v2')),
    url(r'^', include(bulk_router.urls, namespace='')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^panel-price/', masterViews.CarPanelPriceAPIView.as_view(), name="panel-price"),
    url(r'^master-data/', masterViews.MasterDataAPIView.as_view(), name='master_data'),
    url(r'^get-cognito-token/', userViews.APICognitoView.as_view(), name='aws_cognito'),
    url(r'^account-summary/', userViews.UserAccountSummary.as_view(), name='account_summary'),
    #url(r'^social-signup/$', userViews.SocialSignUp.as_view(), name="social_sign_up"),
    #url(r'^auth/', include('rest_framework_social_oauth2.urls')),
]