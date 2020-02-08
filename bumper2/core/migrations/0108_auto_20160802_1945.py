# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0107_auto_20160802_1934'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingdiscount',
            name='material_discount',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingdiscount',
            name='part_discount',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
    ]
