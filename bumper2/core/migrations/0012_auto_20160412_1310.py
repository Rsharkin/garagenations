# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20160412_1306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookingpackage',
            name='actual_price',
        ),
        migrations.RemoveField(
            model_name='bookingpackage',
            name='estimate_price',
        ),
    ]
