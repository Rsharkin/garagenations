# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_auto_20160506_1823'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingCheckpoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='last_status',
            field=models.ForeignKey(related_name='booking_laststatus', to='core.BookingStatus', null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='last_substatus',
            field=models.ForeignKey(related_name='booking_lastsubstatus', to='core.BookingSubStatus', null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='status_updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='sub_status_updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='bookingstatus',
            name='category',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookingstatus',
            name='is_checkpoint',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='last_status',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingStatus', null=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='last_substatus',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingSubStatus', null=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='status_updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='sub_status_updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.ForeignKey(related_name='booking_status', to='core.BookingStatus'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='sub_status',
            field=models.ForeignKey(related_name='booking_sub_status', to='core.BookingSubStatus', null=True),
        ),
        migrations.AlterField(
            model_name='historicalpayment',
            name='payment_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Pay Now'), (1, b'Cash on Delivery')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Pay Now'), (1, b'Cash on Delivery')]),
        ),
        migrations.AddField(
            model_name='bookingcheckpoint',
            name='booking',
            field=models.ForeignKey(related_name='booking_checkpoint', to='core.Booking'),
        ),
    ]
