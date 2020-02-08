__author__ = 'anuj'

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, generics, status
from rest_framework.decorators import list_route, detail_route
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.response import Response
from api.permissions import IsAdminUser
from api.custom_filters import CustomSearchFilter

from core.models.master import (
    City,
    State,
    CarBrand,
    CarModel,
    Package,
    PackagePrice,
    CarPanelPrice,
    BookingStatus,
    BookingOpsStatus,
    CancellationReasons,
    Workshop,
    InternalAccounts,
    FollowupResult,
    CarPanel,
    DelayReasons,
    CarReturnReasons,
    Source,
    TeamAlertReason,
    QualityCheckCategory,
    HandoverItem,
    ChecklistItem,
    DiscountReasons,
    DeliveryReasons,
    FlagType,
    PartDocStatus,
    PartVendor
)
from core.models.booking import Booking
from core.models.payment import Payment
from core.models.users import BumperUser, UserInquiry, Followup, ScratchFinderLead
from api.serializers import masterSerializers
from api.serializers.bookingSerializers import BookingStatusSerializer, BookingOpsStatusSerializer
from api.custom_filters import PackageFilter, CarPanelPriceFilter
from collections import OrderedDict
from api.api_views.custom_mixins import LoggingMixin


class CityViewSet(LoggingMixin,viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows city to be viewed or edited.
    """
    #authentication_classes = (TokenAuthentication,JSONWebTokenAuthentication)
    permission_classes = ()
    queryset = City.objects.filter(active=True).select_related('state')
    serializer_class = masterSerializers.CitySerializer


class StateViewSet(LoggingMixin,viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows state to be viewed or edited.
    """
    #authentication_classes = (TokenAuthentication,JSONWebTokenAuthentication)
    permission_classes = ()
    queryset = State.objects.all().order_by('-active')
    serializer_class = masterSerializers.StateSerializer


class CarBrandViewSet(LoggingMixin,viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows car brand to be viewed or edited.
    """
    #authentication_classes = (TokenAuthentication,JSONWebTokenAuthentication)
    permission_classes = ()
    queryset = CarBrand.objects.all().order_by('-active')
    serializer_class = masterSerializers.CarBrandSerializer


class CarModelViewSet(LoggingMixin,viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows car model to be viewed or edited.
    """
    #authentication_classes = (TokenAuthentication,JSONWebTokenAuthentication)
    permission_classes = ()
    queryset = CarModel.objects.filter(
                            active=True,
                            parent__isnull=True).select_related(
                                                    'brand').prefetch_related('colors',
                                                                              'variants').order_by('-active')
    serializer_class = masterSerializers.CarModelSerializer
    filter_backends = (DjangoFilterBackend, CustomSearchFilter)
    filter_fields = ('name', 'active', 'brand_id', 'popular')
    search_fields = ('name', 'brand__name')

    @detail_route(methods=['get'], url_path='model-by-year')
    def get_car_model_by_year(self, request, pk=None):
        """
            This API will give car model by year
        """
        input_serializer = masterSerializers.YearSerializer(data=request.query_params)
        if input_serializer.is_valid():
            input_data = input_serializer.validated_data
            instance = self.get_object()
            car_model = instance.get_car_model_by_year(input_data.get('year'))
            serializer = self.get_serializer(car_model)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PackageViewSet(LoggingMixin,viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows car brand to be viewed or edited.
    """
    #authentication_classes = (TokenAuthentication,JSONWebTokenAuthentication)
    permission_classes = ()
    queryset = Package.objects.all()
    serializer_class = masterSerializers.PackageSerializer


class CarPanelViewSet(LoggingMixin,viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows car brand to be viewed or edited.
    """
    #authentication_classes = (TokenAuthentication,JSONWebTokenAuthentication)
    permission_classes = ()
    queryset = CarPanel.objects.filter(active=True).order_by('sort_order')
    serializer_class = masterSerializers.CarPanelSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('part_type', 'internal')


class PackagePriceViewSet(LoggingMixin,viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows car model to be viewed or edited.
    """
    authentication_classes = (TokenAuthentication,JSONWebTokenAuthentication)
    permission_classes = ()
    queryset = PackagePrice.objects.filter(package__active=True).select_related('package')
    serializer_class = masterSerializers.PackagePriceSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = PackageFilter
    #filter_fields = ('car_type',)

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """

        if self.request.user and self.request.user.groups.filter(name='OpsUser').exists():
            queryset = PackagePrice.objects.filter(package__active=True)
        else:
            queryset = PackagePrice.objects.filter(package__active=True)
            user = self.request.user
            if not user.is_anonymous() and not self.request.query_params.get('city'):
                if user.city:
                    queryset = queryset.filter(city=user.city)
        queryset = queryset.select_related('package')
        params = self.request.query_params
        if params.get('internal') not in ["True", "true"]:
            queryset = queryset.filter(package__internal=False)
        queryset = queryset.order_by('package__sort_order')
        return queryset


class CarPanelPriceAPIView(LoggingMixin,generics.ListAPIView):
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = ()
    serializer_class = masterSerializers.CarPanelPriceSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = CarPanelPriceFilter

    def get_queryset(self):
        queryset = CarPanelPrice.objects.filter(active=True).order_by('car_model_id',
                                                                      'car_model__parent_id',
                                                                      'car_type'
                                                                      ).select_related('car_panel',
                                                                                       'car_model__brand')
        params = self.request.query_params
        if params.get("internal") not in ["True", "true"]:
            queryset = queryset.filter(car_panel__internal=False, internal=False)
        if not params.get('part_type'):
            queryset = queryset.filter(car_panel__part_type=CarPanel.PART_PANEL)
        if params.get("fbb") != "True":
            queryset = queryset.exclude(type_of_work=CarPanelPrice.TYPE_OF_WORK_REPLACE_FBB)
        else:
            # if fbb is True, then remove replace but only for panels.
            queryset = queryset.exclude(type_of_work=CarPanelPrice.TYPE_OF_WORK_REPLACE,
                                        car_panel__part_type=CarPanel.PART_PANEL)
        if self.request.user and self.request.user.groups.filter(name='OpsUser').exists():
            return queryset
        else:
            user = self.request.user
            if not user.is_anonymous() and not self.request.query_params.get('city'):
                if user.city:
                    queryset = queryset.filter(city=user.city)

        # queryset = queryset.extra(select={
        #     'car_model_null': 'car_model_id IS NULL',
        #     'type_of_work_order': "FIND_IN_SET(type_of_work, '" + ",".join(
        #         str(i) for i in CarPanelPrice.TYPE_OF_WORK_ORDERING) + "')",
        #     },
        #     order_by=['car_panel__name', 'car_model_null', 'car_model_id', 'type_of_work_order'],
        #     )
        return queryset

    def get(self, request, *args, **kwargs):
        """
        Return a list of all car panels.
        """
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)

        # to show results based on type of work ordering
        work_order_dict = {type_of_work: index for index, type_of_work in enumerate(CarPanelPrice.TYPE_OF_WORK_ORDERING)}

        # removing the car type prices if model prices exist (sorting first so that car type data comes first)
        d = {}
        for l in serializer.data:
            #key = l['car_panel']['name']+'-'+l['type_of_work']
            key = '{car_panel[name]}-{type_of_work}'.format(**l)
            #if d.get(key, {"car_type": 100}).get('car_type'):
            d[key] = l

        results = d.values()
        results = sorted(results, key=lambda datum: (datum['car_panel']['sort_order'],
                                                     work_order_dict.get(datum['type_of_work_val'],100)))

        # grouping the results at panel level.
        d = OrderedDict()
        for l in results:
            car_panel = l.pop('car_panel')
            car_panel_name = car_panel.pop('name')
            car_panel['panel_id'] = car_panel.pop('id')
            l.update(car_panel)
            d.setdefault(car_panel_name,[]).append(l)

        # creating dict such that panel name is key and price_list is array of all the panel prices.
        results = []
        for key,value in d.iteritems():
            #value = sorted(value, key=lambda  datum: datum['price'])
            results.append({"name":key,"price_list":value})

        # ordering on panel name
        # results = sorted(results, key=lambda datum: (datum.get('name')))

        return Response({"results":results})


class QualityCheckViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """
        API endpoint that allows QC list to be viewed based on category.
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = ()
    queryset = QualityCheckCategory.objects.filter(active=True).order_by('order_num')
    serializer_class = masterSerializers.QualityCheckCategorySerializer


class HandoverItemViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """
        API endpoint that allows handover item list to be viewed.
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = ()
    queryset = HandoverItem.objects.filter(active=True).order_by('order_num')
    serializer_class = masterSerializers.HandoverItemSerializer


class ChecklistItemViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """
        API endpoint that allows checklist item list to be viewed.
    """
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = ()
    queryset = ChecklistItem.objects.filter(active=True, category__active=True).order_by('order_num')
    serializer_class = masterSerializers.ChecklistItemSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('category','category__is_qc')


class PartVendorViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """
        API endpoint that allows part vendor list to be viewed.
    """
    def get_serializer_class(self):
        serializer_class = masterSerializers.GenericModelSerializer
        serializer_class.Meta.model = PartVendor
        return serializer_class

    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = (IsAdminUser,)
    queryset = PartVendor.objects.filter(active=True)
    # serializer_class = masterSerializers.PartVendorSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['city']


class MasterDataAPIView(LoggingMixin, APIView):
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication)
    permission_classes = (IsAdminUser,)

    def get(self, request, format=None):
        """
            Return various master data.
        """
        city_id = request.query_params.get('city_id')
        statuses = BookingStatus.objects.all().select_related('category')
        ops_statuses = BookingOpsStatus.objects.all()
        cancellation_reasons = CancellationReasons.objects.filter(reason_owner=CancellationReasons.REASON_OWNER_OPS,
                                                                  active=True).order_by('order_num')
        sources = dict(Booking.BOOKING_SOURCES)
        user_sources = dict(BumperUser.USER_SOURCES)
        workshops = Workshop.objects.filter(active=True)
        if city_id:
            workshops = workshops.filter(city_id=city_id)
        discount_reasons = DiscountReasons.objects.all()
        delivery_reasons = DeliveryReasons.objects.all()
        part_doc_statuses = PartDocStatus.objects.filter(active=True).order_by('order_num')

        return Response({
            "statuses": BookingStatusSerializer(statuses,many=True).data,
            "sources": sources,
            "user_sources": user_sources,
            "user_inquiry_statuses": dict(UserInquiry.INQUIRY_STATUSES),
            "ops_statuses": BookingOpsStatusSerializer(ops_statuses,many=True).data,
            "cancellation_reasons": masterSerializers.CancellationReasonsSerializer(cancellation_reasons,
                                                                                    many=True).data,
            "workshops": masterSerializers.WorkshopSerializer(workshops, many=True).data,
            "internal_accounts": InternalAccounts.objects.values_list('phone', flat=True).all(),
            "followup_results": masterSerializers.FollowupResultSerializer(FollowupResult.objects.all(),
                                                                           many=True).data,
            "followup_comm_modes": dict(Followup.COMM_MODES),
            "type_of_works": dict(CarPanelPrice.TYPE_OF_WORKS),
            "delay_reasons": masterSerializers.DelayReasonsSerializer(DelayReasons.objects.all(),many=True).data,
            "return_reasons": masterSerializers.ReturnReasonsSerializer(CarReturnReasons.objects.all(),many=True).data,
            "new_sources": masterSerializers.SourceSerializer(Source.objects.filter(active=True), many=True).data,
            "team_alert_reasons": masterSerializers.TeamAlertReasonSerializer(TeamAlertReason.objects.all(),
                                                                              many=True).data,
            "payment_modes": dict(Payment.PAYMENT_MODES),
            "payment_vendors": dict(Payment.VENDOR_LIST),
            "sfl_statuses": dict(ScratchFinderLead.STATUS_CHOICES),
            "discount_reasons": masterSerializers.DiscountReasonsSerializer(discount_reasons, many=True).data,
            "delivery_reasons": masterSerializers.DeliveryReasonsSerializer(delivery_reasons, many=True).data,
            "part_doc_statuses": masterSerializers.PartDocStatusSerializer(part_doc_statuses, many=True).data,
            "flag_types": masterSerializers.FlagTypeSerializer(FlagType.objects.filter(active=True),
                                                               many=True).data
        })