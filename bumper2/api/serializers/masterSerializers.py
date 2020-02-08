__author__ = 'anuj'

from core.models.master import (
    City,
    State,
    CarBrand,
    CarModel,
    Package,
    PackagePrice,
    CarPanel,
    CarPanelPrice,
    Workshop,
    CancellationReasons,
    FollowupResult,
    DelayReasons,
    CarReturnReasons,
    Source,
    QualityCheck,
    QualityCheckCategory,
    TeamAlertReason,
    HandoverItem,
    ChecklistItem,
    DiscountReasons,
    FlagType,
    PartDocStatus,
    DeliveryReasons,
    CarColor,
    CarModelVariant
)

from core.models.coupons import Coupon

from rest_framework import serializers
from commonSerializers import DynamicFieldsModelSerializer
from core.managers.masterManager import get_obj_price, get_obj_dealer_price, get_photo_url
import decimal


class StateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = State
        fields = ('name',)


class CitySerializer(DynamicFieldsModelSerializer):
    state = StateSerializer()
    class Meta:
        model = City
        fields = ('id', 'name', 'state', 'is_denting_active', 'is_wash_active', 'active',
                  'state_code', 'state_name', 'gstin', 'invoice_address')


class CarBrandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CarBrand
        fields = ('name',)


class CarColorSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CarColor
        fields = ('__all__')


class CarModelVariantSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CarModelVariant
        fields = ('__all__')


class CarModelSerializer(DynamicFieldsModelSerializer):
    brand = CarBrandSerializer()
    sized_photo = serializers.SerializerMethodField()
    colors = CarColorSerializer(many=True, read_only=True, new_fields=['id', 'color_name'])
    variants = CarModelVariantSerializer(many=True, read_only=True, new_fields=['id', 'name'])

    class Meta:
        model = CarModel
        fields = ('__all__')

    def get_sized_photo(self, obj):
        return get_photo_url(self.context.get('request'),obj)

    def validate_name(self, value):
        """
            Check that the car name is utf-8 encoding. if not return error.
        """
        try:
            value = value.encode('utf-8')
        except UnicodeDecodeError:
            raise serializers.ValidationError("Invalid search")
        return value


class PackageSerializer(DynamicFieldsModelSerializer):
    # city_id = serializers.PrimaryKeyRelatedField(
    #     queryset=City.objects.all(), source='city', allow_null=True)
    sized_photo = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ('name','photo', 'desc','long_desc','category','pickup_type',
                  'is_doorstep','active','internal','desc_url', 'website_desc_url','sized_photo')

    def get_sized_photo(self, obj):
        return get_photo_url(self.context.get('request'),obj)


class PackagePriceSerializer(DynamicFieldsModelSerializer):
    package = PackageSerializer()
    price = serializers.SerializerMethodField()
    dealer_price = serializers.SerializerMethodField()

    class Meta:
        model = PackagePrice
        fields = ('__all__')

    def get_price(self, obj):
        return str(get_obj_price(obj))

    def get_dealer_price(self, obj):
        return str(get_obj_dealer_price(obj))

    def to_representation(self, obj):
        if self.fields.get('city'):
            self.fields['city'] = CitySerializer()
        return super(PackagePriceSerializer, self).to_representation(obj)


class CarPanelSerializer(DynamicFieldsModelSerializer):
    # photo_thumbnail = serializers.ImageField(read_only=True)
    sized_photo = serializers.SerializerMethodField()
    class Meta:
        model = CarPanel
        fields = ('__all__')

    def get_sized_photo(self, obj):
        return get_photo_url(self.context.get('request'),obj)


class CarPanelPriceSerializer(DynamicFieldsModelSerializer):
    car_panel = CarPanelSerializer()
    type_of_work = serializers.SerializerMethodField()
    type_of_work_val = serializers.IntegerField(source='type_of_work')
    price = serializers.SerializerMethodField()
    new_price = serializers.SerializerMethodField()
    new_price_text = serializers.SerializerMethodField()
    dealer_price = serializers.SerializerMethodField()
    disabled = serializers.SerializerMethodField()
    sized_photo = serializers.SerializerMethodField()

    class Meta:
        model = CarPanelPrice
        fields = ('__all__')

    def get_sized_photo(self, obj):
        return get_photo_url(self.context.get('request'),obj)

    def get_disabled(self, obj):
        request = self.context.get('request')
        if request:
            fbb = request.query_params.get('fbb')
            if fbb == 'True' and obj.type_of_work in (CarPanelPrice.TYPE_OF_WORK_REPLACE,
                                                      CarPanelPrice.TYPE_OF_WORK_DENT,
                                                      CarPanelPrice.TYPE_OF_WORK_SCRATCH,
                                                      CarPanelPrice.TYPE_OF_WORK_PAINT_ONLY):
                if obj.car_panel.part_type == CarPanel.PART_SPARE_PART and obj.type_of_work == CarPanelPrice.TYPE_OF_WORK_REPLACE:
                    return False
                return True
        return False

    def get_type_of_work(self,obj):
        return obj.get_type_of_work_display()

    def get_price(self, obj):
        """
        This is now temporary field just to make sure existing apps don't fail.
        """
        price = str(get_obj_price(obj))
        if obj.type_of_work in [CarPanelPrice.TYPE_OF_WORK_REPLACE, CarPanelPrice.TYPE_OF_WORK_REPLACE_FBB]:
            return str(decimal.Decimal('0.00'))
        else:
            return price

    def get_new_price(self, obj):
        return str(get_obj_price(obj))

    def get_new_price_text(self, obj):
        import locale
        locale.setlocale(locale.LC_ALL, 'en_IN')
        price = "{:n}".format(int(get_obj_price(obj)))
        if obj.type_of_work in [CarPanelPrice.TYPE_OF_WORK_REPLACE, CarPanelPrice.TYPE_OF_WORK_REPLACE_FBB]:
            if obj.part_price is None and obj.material_price is None and obj.labour_price is None:
                return "Part MRP*"
            elif obj.part_price is None:
                return "&#8377; " + price + " + Part MRP"
        return "&#8377; " + price

    def get_dealer_price(self, obj):
        return str(get_obj_dealer_price(obj))


class WorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = ('__all__')


class CancellationReasonsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CancellationReasons
        fields = ('__all__')


class FollowupResultSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FollowupResult
        fields = ('__all__')


class DelayReasonsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = DelayReasons
        fields = ('__all__')


class ReturnReasonsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CarReturnReasons
        fields = ('__all__')


class SourceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Source
        fields = ('__all__')


class QualityCheckSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = QualityCheck
        fields = ('id', 'quality_check', 'order_num')


class QualityCheckCategorySerializer(DynamicFieldsModelSerializer):
    quality_checks_list = QualityCheckSerializer(many=True, required=False)

    class Meta:
        model = QualityCheckCategory
        fields = ('category', 'order_num','quality_checks_list')


class TeamAlertReasonSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = TeamAlertReason
        fields = ('__all__')


class HandoverItemSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = HandoverItem
        fields = ('__all__')


class ChecklistItemSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ('__all__')


class DiscountReasonsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = DiscountReasons
        fields = ('__all__')


class FlagTypeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = FlagType
        fields = ('__all__')


class CouponSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Coupon
        fields = ('__all__')


class GenericModelSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = None
        fields = ('__all__')


class PartDocStatusSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = PartDocStatus
        fields = ('__all__')


class DeliveryReasonsSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = DeliveryReasons
        fields = ('__all__')


class YearSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=True, min_value=1900)
