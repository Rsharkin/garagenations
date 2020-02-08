__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from core.models.booking import *
from core import constants

def update_booking_package(bp):
    from decimal import Decimal
    if bp.price and bp.package.package.category != 2:
        bp.material_price = (bp.price * Decimal("0.3")).quantize(constants.TWO_PLACES)
        bp.labour_price = (bp.price - bp.material_price).quantize(constants.TWO_PLACES)
        # bp.part_vat = (constants.VAT_FACTOR * bp.part_price)
        # bp.part_price = bp.part_price - bp.part_vat
        bp.save()
    for bpp in bp.booking_package_panel.all():
        if bpp.price and bpp.panel.type_of_work != 3:
            bpp.material_price = (bpp.price * Decimal("0.3")).quantize(constants.TWO_PLACES)
            bpp.labour_price = (bpp.price - bpp.material_price).quantize(constants.TWO_PLACES)
            # bpp.part_vat = (constants.VAT_FACTOR * bpp.part_price)
            # bpp.part_price = bpp.part_price - bpp.part_vat
            bpp.save()


bookings = Booking.objects.all()
for b in bookings:
    for bp in b.booking_package.all():
        update_booking_package(bp)
