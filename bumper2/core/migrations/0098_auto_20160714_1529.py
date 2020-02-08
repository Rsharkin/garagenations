# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_auto_20160713_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='drop_slot_end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='pickup_slot_end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='drop_slot_end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='pickup_slot_end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
