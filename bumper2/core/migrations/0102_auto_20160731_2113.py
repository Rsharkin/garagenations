# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'anuj'

from django.db import migrations
#from core.models.booking import Booking
from decimal import Decimal

def update_booking_prices(apps, schema_editor):
    """
    For all bookings, change price of each package and panel.
    """
    Booking = apps.get_model('core','Booking')
    bookings = Booking.objects.all().prefetch_related('booking_package','booking_package__booking_package_panel')
    for booking in bookings:
        booking_packages = booking.booking_package.all()
        for booking_package in booking_packages:
            booking_package.part_price = booking_package.part_price + booking_package.part_vat
            booking_package.material_price = booking_package.material_price + booking_package.material_vat
            booking_package.labour_price = booking_package.labour_price + booking_package.labour_service_tax + \
                                            booking_package.labour_kk_tax + booking_package.labour_sb_tax
            booking_package.save()
            for bpp in booking_package.booking_package_panel.all():
                bpp.part_price = bpp.part_price + bpp.part_vat
                bpp.material_price = bpp.material_price + bpp.material_vat
                bpp.labour_price = bpp.labour_price + bpp.labour_service_tax + \
                                   bpp.labour_kk_tax + bpp.labour_sb_tax
                bpp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0101_auto_20160721_1320'),
    ]

    operations = [
        migrations.RunPython(update_booking_prices, reverse_code=migrations.RunPython.noop),
    ]
