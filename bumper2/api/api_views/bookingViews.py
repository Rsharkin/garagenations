__author__ = 'anuj'

from django.db.models import Q
from rest_framework import viewsets, filters, mixins, views
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import list_route, detail_route
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from api.custom_paginations import PageNumberPaginationDataOnly
from rest_framework.parsers import FormParser, MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend

from api.custom_auth import BookingAuthentication
from api.permissions import (
    IsOwnerOrAdmin,
    BookingIsOwnerOrAdmin,
    BookingPackageIsOwnerOrAdmin,
    HasGroupPermission,
    IsAdminUser,
    IsDriver,
    IsBookingDriver,
    IsWorkshopExecutive,
    PermissionOneOf
)

from api.serializers.masterSerializers import CouponSerializer

from api.serializers.bookingSerializers import (
    BookingSerializer,
    BookingPackageSerializer,
    BookingPackagePanelSerializer,
    GetSlotSerializer,
    BookingAddressSerializer,
    BookingBillSerializer,
    PaymentSerializer,
    FollowupSerializer,
    InitiatePaymentSerializer,
    BookingStatusSerializer,
    ProcessPaymentSerializer,
    CouponDetailSerializer,
    DriverBookingSerializer,
    BookingImageSerializer,
    BookingDiscountSerializer,
    BookingCouponSerializer,
    BookingListSerializer,
    BookingBillSerializerV2,
    BookingCartSerializer,
    BookingFollowupSerializer,
    BookingFeedbackSerializer,
    BookingCustFeedbackSerializer,
    EODNoticeSerializer,
    BookingProformaInvoiceSerializer,
    SaveEODSerializer,
    BookingReworkPackagePanelSerializer,
    BookingReworkPackageSerializer,
    WorkshopBookingSerializer,
    BookingQualityCheckSerializer,
    BookingTestedQualityCheckSerializer,
    EntityChangeTrackerSerializer,
    TeamAlertSerializer,
    BookingHandoverCreateSerializer,
    BookingHandoverSerializer,
    BookingChecklistSerializer,
    BookingChecklistCreateSerializer,
    BookingFlagSerializer,
    BookingPartDocSerializer,
    BookingPartQuoteSerializer,
    BPPHistorySerializer,
    BookingExpectedEODSerializer
)

from core.models.payment import Payment
from core.models.users import WorkshopUser
from core.models.booking import (
    Booking,
    BookingPackage,
    BookingPackagePanel,
    BookingAddress,
    BookingCoupon,
    BookingImage,
    BookingDiscount,
    BookingInvoice,
    BookingFeedback,
    BookingCustFeedback,
    BookingProformaInvoice,
    BookingReworkPackagePanel,
    BookingReworkPackage,
    BookingQualityChecks,
    EntityChangeTracker,
    TeamAlert,
    BookingHandoverItem,
    BookingChecklist,
    BookingFlag,
    BookingPartDoc,
    BookingPartQuote,
    BookingExpectedEOD
)

from core.models.master import BookingStatus, Notifications, CancellationReasons, Hooks, Source

from core.managers.bookingManager import get_pickup_slots, get_drop_slots
from api.custom_filters import BookingFilter, BookingChecklistFilter, BPPHistoryFilter
from api.api_views.custom_mixins import LoggingMixin, CreateListModelMixin
from api import custom_auth
from core.managers import paymentManager, bookingManager
from core.tasks import send_custom_notification_task

import logging
logger = logging.getLogger(__name__)


class BookingViewSet(LoggingMixin,
                     viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsOwnerOrAdmin,)
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = BookingFilter
    #filter_fields = ('id', 'usercar', 'status')
    pagination_class = PageNumberPagination
    permissions_list = []

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == 'get_booking_list' or self.action == 'generate_payment_link':
            serializer_class = BookingListSerializer
        elif self.action == 'get_cart_details':
            serializer_class = BookingCartSerializer
        elif self.action == 'followup':
            serializer_class = BookingFollowupSerializer
        elif self.action == 'get_booking_from_token':
            serializer_class = BookingBillSerializerV2
        # elif self.action == 'rework_details':
        #     serializer_class = BookingReworkSerializer
        return serializer_class

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            queryset = Booking.objects.all()
        else:
            queryset = Booking.objects.filter(user=self.request.user)
        params = self.request.query_params
        internal = False
        # TODO: REMOVE INTERNAL FLAG STRING TRUE AFTER FORCED VERSION - ANDROID_VERSION_CODE = 58
        if params.get('internal') in ["True", "true"] \
                or self.action in ('update','partial_update',
                                   'add_coupon','get_coupon_details',
                                   'save_invoice', 'rework_details'):
            internal = True
        if (self.action == 'followup' and self.request.method == 'PATCH') or (self.action == 'rework_details' or
                self.action == 'get_slots' or self.action == 'initiate_payment' or
                self.action == 'generate_payment_token'
                ):
            pass
        else:
            queryset = self.get_serializer_class().setup_eager_loading(queryset, internal)
        return queryset

    def perform_create(self, serializer):
        vdata = serializer.validated_data
        user = self.request.user
        if vdata.get('user') and self.request.user.groups.filter(name='OpsUser').exists():
            user = vdata.get('user')
        if not vdata.get('source') and self.request.META.get('HTTP_SOURCE'):
            vdata['source'] = Source.objects.filter(source=self.request.META.get('HTTP_SOURCE')).first()
        serializer.save(user=user)

    @list_route(methods=['get'])
    def get_slots(self, request):
        """
            get pickup slots
        """
        serializer = GetSlotSerializer(data=request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            if data.get('type') == BookingAddress.ADDRESS_TYPE_PICKUP:
                slots = get_pickup_slots(data)
            else:
                slots = get_drop_slots(data)
            return Response(slots, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=(IsOwnerOrAdmin,))
    def initiate_payment(self, request, pk=None):
        """
            pay cash on delivery
        """
        logger.info("Initiate Payment : data: %s, booking_id: %s" % (request.data, pk))
        booking = self.get_object()
        serializer = InitiatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            invoice = BookingInvoice.objects.filter(booking=booking,status=BookingInvoice.INVOICE_STATUS_PENDING).first()
            if invoice:
                p = Payment.objects.filter(invoice=invoice,tx_status=Payment.TX_STATUS_PENDING,
                                           payment_type=data.get('payment_type')).first()
                if not p:
                    p = Payment.objects.create(
                            invoice=invoice,
                            tx_status=Payment.TX_STATUS_PENDING,
                            payment_type=data.get('payment_type'),
                            device_type=self.request.META.get('HTTP_SOURCE')
                        )

                    # if data.get('payment_type') == Payment.PAYMENT_TYPE_COD:
                    #     booking.status_id = 18
                    #     booking.updated_by = request.user
                    #     booking.save()
                return Response(PaymentSerializer(p).data,status=status.HTTP_200_OK)
            else:
                return Response("No pending invoice exist for this booking", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=(IsOwnerOrAdmin,))
    def initiate_payment_proforma(self, request, pk=None):
        """
            pay cash on delivery
        """
        logger.info("Initiate Payment For proforma invoice: data: %s, booking_id: %s" % (request.data, pk))
        booking = self.get_object()
        serializer = InitiatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            proforma_invoice = BookingProformaInvoice.objects.filter(booking=booking,
                                                       status=BookingProformaInvoice.INVOICE_STATUS_PENDING).first()
            if proforma_invoice:
                p = Payment.objects.filter(proforma_invoice=proforma_invoice, tx_status=Payment.TX_STATUS_PENDING,
                                           payment_type=data.get('payment_type')).first()
                if not p:
                    p = Payment.objects.create(
                        proforma_invoice=proforma_invoice,
                        tx_status=Payment.TX_STATUS_PENDING,
                        payment_type=data.get('payment_type'),
                        device_type=self.request.META.get('HTTP_SOURCE')
                    )
                    # if data.get('payment_type') == Payment.PAYMENT_TYPE_COD:
                    #     booking.status_id = 18
                    #     booking.updated_by = request.user
                    #     booking.save()
                return Response(PaymentSerializer(p).data, status=status.HTTP_200_OK)
            else:
                return Response("No pending proforma invoice exist for this booking", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[PermissionOneOf], permissions_list=[IsAdminUser, IsDriver])
    def make_payment(self, request, pk=None):
        """
            pay cash on delivery - This is only allowed for Ops User or Driver.
        """
        logger.info("Make Payment : data: %s, booking_id: %s" % (request.data, pk))
        booking = self.get_object()
        serializer = ProcessPaymentSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['booking_id'] = booking.id
            data['device_type'] = self.request.META.get('HTTP_SOURCE')
            if paymentManager.process_payment_response(data, data.get('vendor_tx_data')):
                if data.get('device_type') == 'opsPanel':
                    send_custom_notification_task.delay('OPS_ADD_PAYMENT_OPS_PANEL',
                                                        {'booking': booking.id,
                                                         'amount': data.get('net_amount_debit'),
                                                         'reason': data.get('tx_data'),
                                                         })
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({"message":"Missing critical data"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'])
    def get_coupon_details(self, request, pk=None):
        """
            given a coupon code and booking, it will return the bill dictionary with discounts due to coupon.
        """
        logger.info("Get Coupon Details : data: %s, booking_id: %s" % (request.query_params, pk))
        booking = self.get_object()
        serializer = CouponDetailSerializer(data=request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            bill_dict, message, coupon = bookingManager.get_bill_with_coupon(booking,data.get('coupon_code'))

            coupon_serializer = CouponSerializer(coupon, new_fields=['valid_until','desc'])
            coupon_detail_dict = coupon_serializer.data

            if message:
                return Response({"message": message, "bill": bill_dict, "coupon_detail": coupon_detail_dict},
                                status=status.HTTP_206_PARTIAL_CONTENT)

            return Response({ "bill": bill_dict, "coupon_detail": coupon_detail_dict}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def add_coupon(self, request, pk=None):
        """
        given a coupon code and booking, it will add that coupon to booking if coupon is valid.
        """
        logger.info("Get Coupon Details : data: %s, booking_id: %s" % (request.data, pk))
        booking = self.get_object()
        serializer = CouponDetailSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            coupon_code = data.get('coupon_code')
            # add coupon when invoice is not created. check validity and add.
            if booking.status.flow_order_num > 13:
                invoice, bill_dict, message = bookingManager.save_invoice(booking, coupon_code=coupon_code)
                discount_dict = bill_dict.get('discount_dict')
            else:
                BookingCoupon.objects.filter(booking=booking).exclude(coupon__code=coupon_code).delete()
                discount_dict, message, coupon = bookingManager.get_coupon_details(booking, coupon_code)
                if coupon and discount_dict:
                    booking_coupon = BookingCoupon.objects.create(coupon=coupon, booking=booking)
                    discount_dict['coupon_id'] = booking_coupon.id
                bill_dict = {'discount_dict': discount_dict}

            if discount_dict:
                return Response({"bill": bill_dict}, status=status.HTTP_200_OK)
            else:
                return Response({"message": message, "bill": bill_dict}, status=status.HTTP_206_PARTIAL_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def alert_booking_changed(self, request, pk=None):
        """
            Send changes in Booking notification to customer.
        """
        logger.info("alert_booking_changed data: %s, booking_id: %s" % (request.data, pk))
        booking = self.get_object()

        if booking:
            from core.constants import ACTION_BOOKING_CHANGED
            #from core.tasks import process_hooks
            from core.managers.generalManager import process_hooks
            process_hooks(pk, ACTION_BOOKING_CHANGED, sent_by_id=request.user.id)
            return Response({"message": "Notifications Sent"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Booking Id is not correct"}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[IsAdminUser])
    def send_eod_notification(self, request, pk=None):
        """

        :param request:
        :param pk:
        :return:
        """
        logger.info("send_eod_notification : data: %s, booking_id: %s" % (request.data, pk))
        booking = self.get_object()
        serializer = EODNoticeSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            action = data.get('action')
            from core.managers.generalManager import process_hooks
            process_hooks(booking.id, action_taken=action, sent_by_id=request.user.id,
                          notice_for=Notifications.NOTICE_FOR_EOD)
            return Response({"message": "Notifications Sent"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[IsAdminUser])
    def save_manually_sent_eod_message(self, request, pk=None):
        """
            Save EOD message that is sent manually
        :param request:
        :return:
        """
        logger.info("save_manually_sent_eod_message : data: %s, booking_id: %s" % (request.data, pk))
        booking = self.get_object()
        serializer = SaveEODSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            from core.managers.generalManager import save_manually_sent_eod_message
            save_manually_sent_eod_message(booking, data, sent_by_id=request.user.id)
            return Response({"message": "Notifications Saved"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], permission_classes=[IsAdminUser])
    def get_eod_notification(self, request, pk=None):
        """

        :param request:
        :param pk:
        :return:
        """
        logger.info("get_eod_notification : data: %s, booking_id: %s" % (request.data, pk))
        booking = self.get_object()

        action_based_on_status = bookingManager.get_action_from_booking(booking)

        if not action_based_on_status:
            return Response({"message": "No valid EOD action for current booking status and ops-status."},
                            status=status.HTTP_200_OK)

        notifications = Hooks.objects.select_related('notification').filter(action_taken=action_based_on_status,
                                                                            notification__notice_for='eod')

        if not notifications:
            return Response({"message": "No valid EOD notification for current booking status and ops-status."},
                            status=status.HTTP_200_OK)

        data = []
        for notice in notifications:
            data.append({
                'name': notice.notification.name,
                'type': dict(Notifications.NOTIFICATION_TYPES).get(notice.notification.type) if notice.notification.type else '',
                'subject': notice.notification.subject,
                'template': notice.notification.template,
            })
        return Response({"data": data, "action_based_on_status": action_based_on_status}, status=status.HTTP_200_OK)

    @list_route(methods=['get'])
    def get_booking_list(self, request):
        """
            This API will give booking list with basic details.
        """
        return super(BookingViewSet, self).list(request)

    @detail_route(methods=['get'])
    def get_cart_details(self, request, pk=None):
        """
            This API will give booking cart details
        """
        return super(BookingViewSet, self).retrieve(request)

    @detail_route(methods=['get','patch'],permission_classes=[IsAdminUser])
    def followup(self, request, pk=None):
        """
            This API will get/save booking followings
        """
        if request.method == 'PATCH':
            return super(BookingViewSet, self).partial_update(request)
        else:
            return super(BookingViewSet, self).retrieve(request)

    @detail_route(methods=['patch'],permission_classes=[IsAdminUser])
    def save_invoice(self, request, pk=None):
        """
            This API will create/update invoice for booking.
        """
        booking = self.get_object()
        bookingManager.save_invoice(booking)
        return Response({"message": "Booking Invoice Updated"}, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=[IsAdminUser])
    def get_payments(self, request, pk=None):
        """
            This API will get payments for booking.
        """
        booking = self.get_object()
        return Response(paymentManager.get_payments(booking), status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=[IsAdminUser])
    def rework_details(self, request, pk=None):
        """
            This API will get the rework details for the booking
        """
        booking = self.get_object()
        return Response(bookingManager.get_rework_details(booking), status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=[IsAdminUser])
    def generate_payment_token(self, request, pk=None):
        """
            This API will get the token.
        """
        booking = self.get_object()
        token = custom_auth.get_booking_token(booking)
        # uri = '{scheme}://{host}/api/booking/get_booking_from_token/?token={token}'.format(scheme=request.scheme,
        #                                                                                host=request.get_host(),
        #                                                                                token=token)
        return Response({'token': token}, status=status.HTTP_200_OK)

    @list_route(methods=['get'], permission_classes=[])
    def get_booking_from_token(self, request, pk=None):
        """
            This API will give booking details from token
        """
        token = request.query_params.get('token')
        booking_id = custom_auth.get_booking_id_from_token(token)
        if booking_id:
            queryset = Booking.objects.filter(id=booking_id)
            queryset = self.get_serializer_class().setup_eager_loading(queryset)
            from django.shortcuts import get_object_or_404
            booking = get_object_or_404(queryset, **{'id': booking_id})
            if booking.status_id in (23,24):
                return Response("Token Expired", status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(booking)
            return Response(serializer.data)
        else:
            return Response("Invalid Token", status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['get'], permission_classes=[IsAdminUser])
    def can_close_booking(self, request, pk=None):
        """
            This API will get the token.
        """
        booking = self.get_object()
        message, allowed = bookingManager.can_close_booking(booking)
        return Response({'allowed': allowed, "message": message}, status=status.HTTP_200_OK)


class BookingPackageViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
        API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (BookingIsOwnerOrAdmin,)
    queryset = BookingPackage.objects.all()
    serializer_class = BookingPackageSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'booking')

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            return BookingPackage.objects.all()
        else:
            return BookingPackage.objects.filter(booking__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        booking = instance.booking
        if booking.status.flow_order_num >= 15:
            return Response("Cannot Delete package after work completed", status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        if not self.request.user.groups.filter(name='OpsUser').exists():
            package_count = BookingPackage.objects.filter(booking=booking).count()
            if package_count == 0:
                booking.status_id = 24
                booking.updated_by = self.request.user
                cancel_reason = CancellationReasons.objects.filter(id=31).first()
                booking.cancel_reason_dd = cancel_reason
                booking.reason_for_cancellation_desc = "Cancelled due to empty cart - System"
                booking.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookingAddressViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (BookingIsOwnerOrAdmin,)
    queryset = BookingAddress.objects.all()
    serializer_class = BookingAddressSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id', 'booking','type', 'useraddress')

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            return BookingAddress.objects.all()
        else:
            return BookingAddress.objects.filter(booking__user=self.request.user)


class BookingBillViewSet(LoggingMixin,viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows booking bill to be viewed
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsOwnerOrAdmin,)
    queryset = Booking.objects.all()
    serializer_class = BookingBillSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = BookingFilter

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.version == 'v2':
            serializer_class = BookingBillSerializerV2
        return serializer_class

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            queryset = Booking.objects.all()
        else:
            queryset = Booking.objects.filter(user=self.request.user)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


class BookingPackagePanelViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows booking package panel to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (BookingPackageIsOwnerOrAdmin,)
    queryset = BookingPackagePanel.objects.all()
    serializer_class = BookingPackagePanelSerializer

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            return BookingPackagePanel.objects.all()
        else:
            return BookingPackagePanel.objects.filter(booking_package__booking__user=self.request.user)

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = kwargs["data"]

            if isinstance(data, list):
                kwargs["many"] = True

        return super(BookingPackagePanelViewSet, self).get_serializer(*args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        booking_package = instance.booking_package
        if booking_package.booking.status.flow_order_num >= 15:
            return Response("Cannot Delete panel after work completed", status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        panel_count = BookingPackagePanel.objects.filter(booking_package=booking_package).count()
        if panel_count == 0:
            booking_package.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows payment to be created
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsAdminUser,)
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('invoice',)


class BookingStatusViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows showing booking statuses
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsAdminUser,)
    queryset = BookingStatus.objects.all()
    serializer_class = BookingStatusSerializer


class DriverBookingViewSet(BookingViewSet):
    """
    API endpoint that allows operations on driver bookings.
    """
    permission_classes = (IsDriver,)
    serializer_class = DriverBookingSerializer

    def get_queryset(self):
        queryset = super(DriverBookingViewSet, self).get_queryset()
        return queryset.filter((Q(is_doorstep=False) & Q(pickup_driver=self.request.user) &
                                (Q(status__flow_order_num__range=(4,9)) |
                                 (Q(status__flow_order_num=3) & Q(ops_status__flow_order_num__range=(3,4))) |
                                 (Q(status__flow_order_num=10) & Q(ops_status__isnull=True)))) |
                               (Q(is_doorstep=False) & Q(drop_driver=self.request.user) &
                                (Q(status__flow_order_num__range=(19,21)))) |
                               (Q(is_doorstep=True) & (Q(drop_driver=self.request.user) |
                                                       Q(pickup_driver=self.request.user)) &
                                (Q(status__flow_order_num__range=(3,21)))))

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BookingImageViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Images to be created for booking
    """
    authentication_classes = (JSONWebTokenAuthentication, BookingAuthentication)
    permission_classes = (BookingIsOwnerOrAdmin, IsBookingDriver)
    queryset = BookingImage.objects.all().select_related('media')
    serializer_class = BookingImageSerializer
    parser_classes = (MultiPartParser, FormParser,)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking',)
    pagination_class = PageNumberPaginationDataOnly

    def get_queryset(self):
        if self.request.user.groups.filter(name='OpsUser').exists():
            queryset = BookingImage.objects.all()
        else:
            if self.request.user.groups.filter(name='Driver').exists():
                queryset = BookingImage.objects.filter(
                    Q(booking__pickup_driver=self.request.user) | Q(booking__drop_driver=self.request.user))
            else:
                if self.request.auth and isinstance(self.request.auth, Booking):
                    queryset = BookingImage.objects.filter(booking=self.request.auth)
                else:
                    queryset = BookingImage.objects.filter(booking__user=self.request.user)
        return queryset.select_related('media', 'updated_by', 'status', 'ops_status', 'panel')

    def perform_create(self, serializer):
        serializer.save(media=self.request.data.get('media'))


class BookingDiscountViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows booking discount to be created.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = BookingDiscount.objects.all()
    serializer_class = BookingDiscountSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking',)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        booking = instance.booking
        instance.delete()
        if booking.status.flow_order_num >= 15:
            bookingManager.save_invoice(booking)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookingCouponViewSet(LoggingMixin,mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows booking discount to be created.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (BookingIsOwnerOrAdmin,)
    queryset = BookingCoupon.objects.all()
    serializer_class = BookingCouponSerializer
    #filter_backends = (DjangoFilterBackend,)
    #filter_fields = ('booking',)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        booking = instance.booking
        instance.delete()
        if booking.status.flow_order_num >= 15:
            bookingManager.save_invoice(booking)
        return Response(status=status.HTTP_204_NO_CONTENT)


# class BookingFollowupViewSet(LoggingMixin, viewsets.ModelViewSet):
#     """
#     API endpoint that allows booking followups to be viewed or created or updated.
#     """
#     authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
#     permission_classes = [HasGroupPermission]
#     required_groups = {
#         'GET': ['OpsUser'],
#         'PATCH': ['OpsUser'],
#     }
#     queryset = Booking.objects.all()
#     serializer_class = BookingFollowupSerializer
#     pagination = None
#
#     def get_queryset(self):
#         queryset = Booking.objects.all()
#         if self.action in ['list','retrieve']:
#             queryset = queryset.prefetch_related(Prefetch(
#                                                     'followup',
#                                                     Followup.objects.order_by('-created_at').select_related('updated_by'),
#                                                 ))
#         return queryset


class BookingFeedbackViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows booking feedback to be created.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = BookingFeedback.objects.all()
    serializer_class = BookingFeedbackSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking',)


class BookingCustFeedbackViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows booking customer feedback to be created.
    """
    authentication_classes = (JSONWebTokenAuthentication,BookingAuthentication)
    permission_classes = (BookingIsOwnerOrAdmin,)
    queryset = BookingCustFeedback.objects.all()
    serializer_class = BookingCustFeedbackSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking',)

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.groups.filter(name='OpsUser').exists():
            return BookingCustFeedback.objects.all()
        else:
            if self.request.auth and isinstance(self.request.auth, Booking):
                return BookingCustFeedback.objects.filter(booking=self.request.auth)
            else:
                return BookingCustFeedback.objects.filter(booking__user=self.request.user)


class BookingProformaInvoiceViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows proforma invoices to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = BookingProformaInvoice.objects.all()
    serializer_class = BookingProformaInvoiceSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking',)


class BookingReworkPackageViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows rework package to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = BookingReworkPackage.objects.all()
    serializer_class = BookingReworkPackageSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking_package')


class BookingReworkPackagePanelViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows rework package to be viewed or edited.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = BookingReworkPackagePanel.objects.all()
    serializer_class = BookingReworkPackagePanelSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking_package_panel',)


class WorkshopBookingViewSet(BookingViewSet):
    """
    API endpoint that allows operations on workshop bookings.
    """
    permission_classes = (IsWorkshopExecutive,)
    serializer_class = WorkshopBookingSerializer

    def get_queryset(self):
        queryset = super(WorkshopBookingViewSet, self).get_queryset()
        workshops = WorkshopUser.objects.filter(user=self.request.user).values_list('workshop_id')
        return queryset.filter(status__flow_order_num__gte=10, workshop__in=workshops,
                               status__flow_order_num__lte=20)


class BookingQualityCheckViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
        API endpoint that allows QC list to be saved against booking.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)
    serializer_class = BookingQualityCheckSerializer
    queryset = BookingQualityChecks.objects.all().select_related('quality_check')
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking',)

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingTestedQualityCheckSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response(status=status.HTTP_201_CREATED)


class EntityChangeTrackerViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
        API endpoint for EntityChangeTracker.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    queryset = EntityChangeTracker.objects.all().order_by('-created_at')
    serializer_class = EntityChangeTrackerSerializer
    permission_classes = [HasGroupPermission]
    required_groups = {
        'POST': ['OpsUser', 'OpsAdmin'],
        'GET': ['OpsUser']
    }
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('item_tracked', 'content_id', 'content_type')


class TeamAlertViewSet(LoggingMixin, CreateListModelMixin, viewsets.ModelViewSet):
    """
        API endpoint for TeamAlert.
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    queryset = TeamAlert.objects.all().select_related('alert_reason','workshop')
    serializer_class = TeamAlertSerializer
    permission_classes = [HasGroupPermission]
    required_groups = {
        'POST': ['OpsUser', 'OpsAdmin', 'WorkshopExecutive', 'Driver'],
        'PATCH': ['OpsUser', 'OpsAdmin', 'WorkshopManager'],
        'GET': ['OpsUser']
    }
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('resolved','workshop')


class BookingHandoverViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
        API endpoint that allows QC list to be saved against booking.
    """
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAdminUser,)
    serializer_class = BookingHandoverSerializer
    queryset = BookingHandoverItem.objects.all().select_related('item')
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking',)

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingHandoverCreateSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response(status=status.HTTP_201_CREATED)


class BookingChecklistViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
        API endpoint that allows QC list to be saved against booking.
    """
    authentication_classes = (JSONWebTokenAuthentication,BookingAuthentication)
    permission_classes = [PermissionOneOf]
    permissions_list = [HasGroupPermission, BookingIsOwnerOrAdmin]
    # permission_classes = [HasGroupPermission]
    required_groups = {
        'POST': ['OpsUser', 'OpsAdmin', 'WorkshopExecutive', 'WorkshopManager', 'Driver'],
        #'PATCH': ['OpsUser', 'OpsAdmin', 'WorkshopManager'],
        'GET': ['OpsUser']
    }
    serializer_class = BookingChecklistSerializer
    queryset = BookingChecklist.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = BookingChecklistFilter
    pagination_class = PageNumberPaginationDataOnly

    def get_queryset(self):
        queryset = BookingChecklist.objects.all().order_by('item__category',
                                                           'status',
                                                           'ops_status',
                                                           'group_num'
                                                           ).select_related('booking',
                                                                            'status',
                                                                            'ops_status',
                                                                            'updated_by',
                                                                            'item__category').prefetch_related('media')
        if not self.request.user.groups.filter(name='OpsUser').exists():
            if self.request.auth and isinstance(self.request.auth, Booking):
                queryset = queryset.filter(booking=self.request.auth)
            else:
                queryset = queryset.filter(booking__user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingChecklistCreateSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response(status=status.HTTP_201_CREATED)


class BookingFlagViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows booking flag to be created.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsAdminUser,)
    queryset = BookingFlag.objects.all()
    serializer_class = BookingFlagSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking',)


class BookingPartDocViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows booking flag to be created.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsAdminUser,)
    queryset = BookingPartDoc.objects.filter().select_related(
                                                'status',
                                                'booking_part__panel__car_panel').prefetch_related(
                                                                                    'notes__updated_by')
    serializer_class = BookingPartDocSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking_part',)


class BookingPartQuoteViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows booking flag to be created.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsAdminUser,)
    queryset = BookingPartQuote.objects.all().select_related('vendor').prefetch_related('notes__updated_by')
    serializer_class = BookingPartQuoteSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking_part_doc','selected')


class BPPHistoryViewSet(LoggingMixin,viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows booking flag to be created.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsAdminUser,)
    queryset = BookingPackagePanel.history.all().select_related('booking_package',
                                                                'panel__car_panel').order_by('-updated_at')
    serializer_class = BPPHistorySerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = BPPHistoryFilter


class BookingExpectedEODViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows booking flag to be created.
    """
    authentication_classes = (JSONWebTokenAuthentication,TokenAuthentication)
    permission_classes = (IsAdminUser,)
    queryset = BookingExpectedEOD.objects.all().order_by('-for_date')
    serializer_class = BookingExpectedEODSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('booking', 'for_date')

