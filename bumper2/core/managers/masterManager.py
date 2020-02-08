__author__ = 'anuj'

import decimal

from core.utils import build_s3_folder_path, build_s3_path


# def round_time(dt=None, roundTo=60):
#     """
#     Round a datetime object to any time laps in seconds
#     roundTo : Closest number of seconds to round to, default 1 minute.
#     """
#     if dt == None : dt = timezone.now()
#     seconds = (dt - dt.min).seconds
#     # // is a floor division, not a comment on following line:
#     rounding = (seconds+roundTo/2) // roundTo * roundTo
#     return dt + timezone.timedelta(0,rounding-seconds+roundTo,-dt.microsecond)


def get_obj_price(obj):
    return ((obj.part_price if obj.part_price is not None else decimal.Decimal('0.00')) +
            (obj.material_price if obj.material_price is not None else decimal.Decimal('0.00')) +
            (obj.labour_price if obj.labour_price is not None else decimal.Decimal('0.00')))


def get_obj_dealer_price(obj):
    return ((obj.dealer_part_price if obj.dealer_part_price is not None else decimal.Decimal('0.00')) +
            (obj.dealer_material_price if obj.dealer_material_price is not None else decimal.Decimal('0.00')) +
            (obj.dealer_labour_price if obj.dealer_labour_price is not None else decimal.Decimal('0.00')))


def get_photo_url(request, obj):
    if request and request.query_params and request.query_params.get('size'):
        return build_s3_folder_path(obj.photo.name, request.query_params.get('size'))
    else:
        if obj.photo:
            if request:
                return request.build_absolute_uri(obj.photo.url)
            else:
                return build_s3_path(obj.photo.name)
    return None
