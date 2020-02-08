# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_remove_bookingpackagepanel_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('address1', models.CharField(max_length=1024)),
                ('address2', models.CharField(help_text=b'this field is updated from dashboard. Will be used to manually save address or landmark', max_length=1024, null=True)),
                ('pin_code', models.IntegerField(null=True)),
                ('area', models.CharField(max_length=128, null=True)),
                ('city', models.CharField(max_length=128, null=True)),
                ('state', models.CharField(max_length=128, null=True)),
                ('country', models.CharField(max_length=128, null=True)),
                ('latitude', models.DecimalField(null=True, max_digits=10, decimal_places=7)),
                ('longitude', models.DecimalField(null=True, max_digits=10, decimal_places=7)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BillItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('service_tax', models.DecimalField(max_digits=10, decimal_places=2)),
                ('vat', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BookingAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, b'Pickup'), (2, b'Drop')])),
                ('address', models.ForeignKey(to='core.Address')),
                ('booking', models.ForeignKey(related_name='booking_address', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BookingBill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('discount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('booking', models.ForeignKey(related_name='booking_bill', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalBookingPackage',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('booking', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.Booking', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('package', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.PackagePrice', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical booking package',
            },
        ),
        migrations.RemoveField(
            model_name='bookingpackage',
            name='price',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='address1',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='address2',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='area',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='city',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='country',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='pin_code',
        ),
        migrations.RemoveField(
            model_name='useraddress',
            name='state',
        ),
        migrations.AlterField(
            model_name='bookingpackagepanel',
            name='panel',
            field=models.ForeignKey(to='core.CarPanelPrice'),
        ),
        migrations.AddField(
            model_name='billitem',
            name='bill',
            field=models.ForeignKey(to='core.BookingBill'),
        ),
        migrations.AddField(
            model_name='billitem',
            name='booking_package',
            field=models.ForeignKey(to='core.BookingPackage'),
        ),
        migrations.AddField(
            model_name='useraddress',
            name='address',
            field=models.ForeignKey(default=1, to='core.Address'),
            preserve_default=False,
        ),
    ]
