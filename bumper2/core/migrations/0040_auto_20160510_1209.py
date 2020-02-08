# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20160509_1828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='actual_drop_address',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='actual_drop_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='actual_pickup_address',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='actual_pickup_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='cancel_reason_dd',
            field=models.ForeignKey(blank=True, to='core.CancellationReasons', null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='desc',
            field=models.CharField(max_length=2048, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='drop_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='estimate_complete_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='estimate_drop_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='estimate_pickup_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='last_status',
            field=models.ForeignKey(related_name='booking_laststatus', blank=True, to='core.BookingStatus', null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='last_substatus',
            field=models.ForeignKey(related_name='booking_lastsubstatus', blank=True, to='core.BookingSubStatus', null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='pickup_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='reason_for_cancellation_desc',
            field=models.CharField(max_length=512, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status_updated_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='sub_status',
            field=models.ForeignKey(related_name='booking_sub_status', blank=True, to='core.BookingSubStatus', null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='sub_status_updated_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='workshop',
            field=models.ForeignKey(blank=True, to='core.Workshop', null=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='actual_drop_address',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='actual_drop_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='actual_pickup_address',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='actual_pickup_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='desc',
            field=models.CharField(max_length=2048, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='drop_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='estimate_complete_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='estimate_drop_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='estimate_pickup_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='pickup_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='reason_for_cancellation_desc',
            field=models.CharField(max_length=512, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='status_updated_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='sub_status_updated_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
