__author__ = 'anuj'
from rest_framework import filters as rest_filters, serializers
from core.models.master import CarModel, PackagePrice, CarPanel, CarPanelPrice
from core.models.users import UserCar
from core.models.booking import Booking, BookingPackage, BookingChecklist, BookingPackagePanel
from core.utils import _convert_naive_datetime_to_given_timezone, _convert_to_given_timezone
from core.managers import bookingManager
from django.contrib.auth import get_user_model
from django.db.models import Q, Max
from datetime import datetime, time
import dateutil.parser
from django_filters.rest_framework import FilterSet
from django_filters import rest_framework as filters
import django_filters


class MultiModelFilterBackend(rest_filters.BaseFilterBackend):
    """
    A filter backend for Multi Models
    """
    def filter_queryset(self, request, queryset, view):
        filter_classes = getattr(view, 'filter_classes', None)

        if filter_classes:
            for filter_class in filter_classes:
                if filter_class._meta.model == queryset.model:
                    queryset = filter_class(request.query_params, queryset=queryset).qs

        return queryset


class ListFilter(filters.CharFilter):

    def sanitize(self, value_list):
        """
        remove empty items in case of ?number=1,,2
        """
        return [v for v in value_list if v != u'']

    def customize(self, value):
        return value

    def filter(self, qs, value):
        multiple_vals = value.split(u",")
        multiple_vals = self.sanitize(multiple_vals)
        multiple_vals = map(self.customize, multiple_vals)
        actual_filter = django_filters.fields.Lookup(multiple_vals, 'in')
        return super(ListFilter, self).filter(qs, actual_filter)


class ListIntegerFilter(ListFilter):
    def customize(self, value):
        try:
            return int(value)
        except ValueError:
            return 0


class PackageFilter(FilterSet):
    car_model = filters.NumberFilter(method='filter_by_car_model', distinct=True)
    usercar_id = filters.NumberFilter(method='filter_by_usercar', distinct=True)
    booking_id = filters.NumberFilter(method='filter_by_booking', distinct=True)
    popular = filters.BooleanFilter(name="package__popular", distinct=True)
    category = filters.NumberFilter(name="package__category", distinct=True)
    #package__city_id = filters.NumberFilter(name="city", distinct=True)

    def filter_by_car_model(self, queryset, name, value):
        cm = CarModel.objects.filter(id=value).first()
        if cm:
            return queryset.filter(car_type=cm.car_type)
        else:
            return queryset.none()

    def filter_by_usercar(self, queryset, name, value):
        uc = UserCar.objects.filter(id=value).select_related('car_model').first()
        if uc:
            return queryset.filter(car_type=uc.car_model.car_type)
        else:
            return queryset.none()

    def filter_by_booking(self, queryset, name, value):
        booking = Booking.objects.filter(id=value).select_related('usercar__car_model').first()
        if booking:
            queryset = queryset.filter(car_type=booking.usercar.car_model.car_type)
            booking_packages = BookingPackage.objects.filter(booking=booking)
            existing_package_ids = []
            for booking_package in booking_packages:
                existing_package_ids.append(booking_package.package_id)
            if existing_package_ids:
                queryset = queryset.exclude(id__in=existing_package_ids)
            return queryset
        else:
            return queryset.none()

    class Meta:
        model = PackagePrice
        fields = ['package__name', 'city', 'car_model', 'car_type', 'usercar_id', 'popular']


class BookingFilter(FilterSet):
    open_booking = filters.MethodFilter(action='filter_by_open_booking', distinct=True)
    pick_drop_date = filters.MethodFilter(action='filter_by_pick_drop_date', distinct=True)
    # user_type = filters.MethodFilter(action='filter_by_user_type', distinct=True)

    def filter_by_open_booking(self, queryset, value):
        if value in ["True","true"]:
            #exclude booking with status booking cancelled or booking closed.
            return bookingManager.filter_open_booking(queryset)
        elif value in ["False", "false"]:
            #only show not open bookings.
            return bookingManager.filter_closed_booking(queryset)
        else:
            return queryset

    def filter_by_pick_drop_date(self, queryset, value):
        from django.conf import settings
        value_date = dateutil.parser.parse(value)
        min_dt = datetime.combine(value_date,time.min)
        max_dt = datetime.combine(value_date,time.max)
        min_dt = _convert_naive_datetime_to_given_timezone(min_dt,tz_name=settings.TIME_ZONE)
        max_dt = _convert_naive_datetime_to_given_timezone(max_dt,tz_name=settings.TIME_ZONE)
        queryset = queryset.filter((Q(pickup_time__gte=min_dt) &
                                   Q(pickup_time__lte=max_dt)) |
                                    (Q(drop_time__gte=min_dt) &
                                   Q(drop_time__lte=max_dt)))
        return queryset

    class Meta:
        model = Booking
        fields = ('id', 'usercar', 'status', 'user', 'city')


class UserFilter(FilterSet):
    group_name = filters.CharFilter(name='groups__name', distinct=True)

    class Meta:
        model = get_user_model()
        fields = ('phone','email', 'group_name', 'is_active')
        ordering_fields = ['name', 'group_name']


class CarPanelPriceFilter(FilterSet):
    usercar = filters.NumberFilter(method='filter_by_usercar', distinct=True)
    carmodel_id = filters.NumberFilter(method='filter_by_car_model', distinct=True)
    # p = filters.NumberFilter(method='filter_by_car_model', distinct=True)  # this is done due to a bug in android
    part_type = ListIntegerFilter(name='car_panel__part_type')

    class Meta:
        model = CarPanelPrice
        fields = ('carmodel_id', 'active', 'usercar', 'city', 'part_type')

    def filter_by_usercar(self, queryset, name, value):
        uc = UserCar.objects.filter(id=value).first()
        if uc:
            queryset = self.filter_by_car_model(queryset, name, uc.car_model_id)
        else:
            queryset = queryset.none()

        return queryset

    def filter_by_car_model(self, queryset, name, value):
        try:
            cm = CarModel.objects.filter(id=value).first()
            if cm and cm.parent:
                queryset = queryset.filter(Q(car_model=cm) | Q(car_type=cm.car_type) | Q(car_model=cm.parent))
            elif cm:
                queryset = queryset.filter(Q(car_model=cm) | Q(car_type=cm.car_type))
            else:
                queryset = queryset.none()
        except:
            queryset = queryset.none()

        return queryset


class BookingChecklistFilter(FilterSet):
    category = filters.NumberFilter(name="item__category")
    is_qc = filters.BooleanFilter(name="item__category__is_qc")
    latest = filters.BooleanFilter(method="filter_by_latest", distinct=True)

    class Meta:
        model = BookingChecklist
        fields = {
            'booking': ['exact'],
            'category': ['exact'],
            'group_num': ['exact'],
            'is_qc': ['exact'],
            'status': ['exact'],
            'ops_status': ['exact', 'isnull'],
            'latest': ['exact'],
        }
        #fields = ('booking', 'category', 'group_num','is_qc', 'status', 'ops_status', 'latest_rec')

    def filter_by_latest(self, queryset, name, value):
        if value:
            max_group_num = queryset.aggregate(Max('group_num'))
            queryset = queryset.filter(group_num=max_group_num['group_num__max'])
        return queryset


class CustomSearchFilter(rest_filters.SearchFilter):
    def get_search_terms(self, request):
        search_terms = super(CustomSearchFilter, self).get_search_terms(request)
        for term in search_terms:
            try:
                term.encode('ascii')
            except UnicodeEncodeError:
                raise serializers.ValidationError("Invalid search")
        return search_terms


class BPPHistoryFilter(FilterSet):
    booking = filters.NumberFilter(name='booking_package__booking', distinct=True)

    class Meta:
        model = BookingPackagePanel.history.model
        fields = ('booking',)
