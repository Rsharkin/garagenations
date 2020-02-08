# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'anuj'

from django.db import models, migrations
from core.models.master import PackagePrice, CarPanelPrice
from decimal import Decimal

def update_package_prices(apps, schema_editor):
    pp_list = PackagePrice.objects.all()
    # part_price for packages will be 0
    # material price will be 0.3 of current price
    # labour price will be 0.7 of current price
    ZERO_PLACES = Decimal("0")
    for pp in pp_list:
        pp.material_price = (pp.price * Decimal('0.3')).quantize(ZERO_PLACES)
        pp.labour_price = (pp.price - pp.material_price).quantize(ZERO_PLACES)
        pp.save()


def update_panel_prices(apps, schema_editor):
    cpp_list = CarPanelPrice.objects.all()
    ZERO_PLACES = Decimal("0")
    for cpp in cpp_list:
        # if not replace panel then update the material price and labour price in 30:70 ratio.
        if cpp.type_of_work != 3:
            cpp.material_price = (cpp.price * Decimal('0.3')).quantize(ZERO_PLACES)
            cpp.labour_price = (cpp.price - cpp.material_price).quantize(ZERO_PLACES)
            cpp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0090_auto_20160708_1133'),
    ]

    operations = [
        migrations.RunPython(update_package_prices, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(update_panel_prices, reverse_code=migrations.RunPython.noop),
    ]
