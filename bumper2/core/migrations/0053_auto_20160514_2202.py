# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0052_auto_20160514_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='drop_driver_start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='pickup_driver_start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='drop_driver_start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='pickup_driver_start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='actual_drop_time',
            field=models.DateTimeField(help_text=b'Car delivered action time', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='actual_drop_time',
            field=models.DateTimeField(help_text=b'Car delivered action time', null=True, blank=True),
        ),
    ]
