# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_auto_20160512_1409'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookingsubstatus',
            options={'ordering': ['flow_order_num'], 'verbose_name_plural': 'Booking Ops Statuses'},
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='sub_status_updated_at',
            new_name='ops_status_updated_at',
        ),
        migrations.RenameField(
            model_name='bookingsubstatus',
            old_name='sub_status',
            new_name='ops_status',
        ),
        migrations.RenameField(
            model_name='bookingsubstatus',
            old_name='sub_status_desc',
            new_name='ops_status_desc',
        ),
        migrations.RenameField(
            model_name='historicalbooking',
            old_name='last_substatus',
            new_name='last_opsstatus',
        ),
        migrations.RenameField(
            model_name='historicalbooking',
            old_name='sub_status',
            new_name='ops_status',
        ),
        migrations.RenameField(
            model_name='historicalbooking',
            old_name='sub_status_updated_at',
            new_name='ops_status_updated_at',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='last_substatus',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='sub_status',
        ),
        migrations.RemoveField(
            model_name='bookingsubstatus',
            name='status',
        ),
        migrations.AddField(
            model_name='booking',
            name='last_opsstatus',
            field=models.ForeignKey(related_name='booking_lastopsstatus', blank=True, to='core.BookingSubStatus', null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='ops_status',
            field=models.ForeignKey(related_name='booking_ops_status', blank=True, to='core.BookingSubStatus', null=True),
        ),
    ]
