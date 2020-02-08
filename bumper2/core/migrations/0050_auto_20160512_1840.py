# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_auto_20160512_1838'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingOpsStatus',
            fields=[
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('ops_status', models.CharField(max_length=128)),
                ('ops_status_desc', models.CharField(max_length=256)),
                ('flow_order_num', models.SmallIntegerField(default=1)),
            ],
            options={
                'ordering': ['flow_order_num'],
                'verbose_name_plural': 'Booking Ops Statuses',
            },
        ),
        migrations.AlterField(
            model_name='booking',
            name='last_opsstatus',
            field=models.ForeignKey(related_name='booking_lastopsstatus', blank=True, to='core.BookingOpsStatus', null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='ops_status',
            field=models.ForeignKey(related_name='booking_ops_status', blank=True, to='core.BookingOpsStatus', null=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='last_opsstatus',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingOpsStatus', null=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='ops_status',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingOpsStatus', null=True),
        ),
        migrations.DeleteModel(
            name='BookingSubStatus',
        ),
    ]
