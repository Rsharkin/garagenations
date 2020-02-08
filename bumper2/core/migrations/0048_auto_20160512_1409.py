# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0047_auto_20160511_2025'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='estimate_drop_time',
            new_name='driver_arrived_drop_time',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='estimate_pickup_time',
            new_name='driver_arrived_pickup_time',
        ),
        migrations.RenameField(
            model_name='historicalbooking',
            old_name='estimate_drop_time',
            new_name='driver_arrived_drop_time',
        ),
        migrations.RenameField(
            model_name='historicalbooking',
            old_name='estimate_pickup_time',
            new_name='driver_arrived_pickup_time',
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
    ]
