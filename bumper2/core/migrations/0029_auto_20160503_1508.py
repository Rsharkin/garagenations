# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20160430_1600'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalPayment',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('payment_for', models.CharField(default=b'user', max_length=6, db_index=True)),
                ('tx_status', models.CharField(max_length=7, choices=[(b'success', b'Success'), (b'failed', b'Failed'), (b'pending', b'Pending')])),
                ('tx_type', models.SmallIntegerField(default=1, choices=[(1, b'Payment'), (2, b'Refund')])),
                ('amount', models.DecimalField(default=0.0, null=True, max_digits=11, decimal_places=2, blank=True)),
                ('mode', models.SmallIntegerField(default=2, choices=[(1, b'Cash'), (2, b'Online'), (3, b'Email Invoice'), (4, b'SMS Link'), (5, b'Cheque'), (6, b'POS')])),
                ('vendor', models.CharField(default=b'PayUMoney', max_length=16, null=True, blank=True, choices=[(b'Citrus', b'By Citrus Pay'), (b'PayUMoney', b'By PayU Money'), (b'bumper', b'Bumper Executive'), (b'UserToDealer', b'User to Dealer Directly'), (b'BumperCitibank', b'By Bumper Citibank'), (b'MSwipe', b'MSwipe POS')])),
                ('payment_vendor_id', models.CharField(help_text=b'This is payuMoneyId in case of PayU. This will be null in case of cash payments', max_length=128, null=True, blank=True)),
                ('refund_vendor_id', models.CharField(help_text=b'Refund for payment, Vendor ID', max_length=128, null=True, blank=True)),
                ('vendor_status', models.CharField(max_length=64, null=True, blank=True)),
                ('error_message', models.CharField(help_text=b'This will reflect error msg from payment gateway if any.', max_length=256, null=True, blank=True)),
                ('cheque_num', models.CharField(max_length=20, null=True, blank=True)),
                ('cheque_bank', models.CharField(max_length=32, null=True, blank=True)),
                ('tx_data', models.TextField(null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical payment',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_for', models.CharField(default=b'user', max_length=6, db_index=True)),
                ('tx_status', models.CharField(max_length=7, choices=[(b'success', b'Success'), (b'failed', b'Failed'), (b'pending', b'Pending')])),
                ('tx_type', models.SmallIntegerField(default=1, choices=[(1, b'Payment'), (2, b'Refund')])),
                ('amount', models.DecimalField(default=0.0, null=True, max_digits=11, decimal_places=2, blank=True)),
                ('mode', models.SmallIntegerField(default=2, choices=[(1, b'Cash'), (2, b'Online'), (3, b'Email Invoice'), (4, b'SMS Link'), (5, b'Cheque'), (6, b'POS')])),
                ('vendor', models.CharField(default=b'PayUMoney', max_length=16, null=True, blank=True, choices=[(b'Citrus', b'By Citrus Pay'), (b'PayUMoney', b'By PayU Money'), (b'bumper', b'Bumper Executive'), (b'UserToDealer', b'User to Dealer Directly'), (b'BumperCitibank', b'By Bumper Citibank'), (b'MSwipe', b'MSwipe POS')])),
                ('payment_vendor_id', models.CharField(help_text=b'This is payuMoneyId in case of PayU. This will be null in case of cash payments', max_length=128, null=True, blank=True)),
                ('refund_vendor_id', models.CharField(help_text=b'Refund for payment, Vendor ID', max_length=128, null=True, blank=True)),
                ('vendor_status', models.CharField(max_length=64, null=True, blank=True)),
                ('error_message', models.CharField(help_text=b'This will reflect error msg from payment gateway if any.', max_length=256, null=True, blank=True)),
                ('cheque_num', models.CharField(max_length=20, null=True, blank=True)),
                ('cheque_bank', models.CharField(max_length=32, null=True, blank=True)),
                ('tx_data', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='drop_driver',
            field=models.ForeignKey(related_name='booking_drop_driver', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='pickup_driver',
            field=models.ForeignKey(related_name='booking_pickup_driver', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='drop_driver',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='pickup_driver',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='booking',
            field=models.ForeignKey(to='core.Booking'),
        ),
        migrations.AddField(
            model_name='historicalpayment',
            name='booking',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.Booking', null=True),
        ),
        migrations.AddField(
            model_name='historicalpayment',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
