# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields
import services.s3.storage
import core.models.common
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20160408_1252'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingPackagePanels',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('dent_type', models.PositiveSmallIntegerField(choices=[(1, b'Scratch'), (2, b'Dent'), (3, b'Paint Only')])),
                ('repair_or_replace', models.BooleanField(default=True)),
                ('booking_package', models.ForeignKey(to='core.BookingPackage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CarModelPanel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('car_model', models.ForeignKey(to='core.CarModel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CarPanelPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('car_type', models.PositiveSmallIntegerField(choices=[(1, b'Hatchback'), (2, b'Sedan'), (3, b'SUV'), (4, b'Luxury')])),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('alias', models.CharField(max_length=128, null=True)),
                ('address1', models.CharField(max_length=1024)),
                ('address2', models.CharField(help_text=b'this field is updated from dashboard. Will be used to manually save address or landmark', max_length=1024, null=True)),
                ('pin_code', models.IntegerField(null=True)),
                ('area', models.CharField(max_length=128, null=True)),
                ('city', models.CharField(max_length=128, null=True)),
                ('state', models.CharField(max_length=128, null=True)),
                ('country', models.CharField(max_length=128, null=True)),
                ('latitude', models.DecimalField(null=True, max_digits=10, decimal_places=7)),
                ('longitude', models.DecimalField(null=True, max_digits=10, decimal_places=7)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('phone', models.CharField(max_length=10, null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('short_address', models.CharField(max_length=128, null=True)),
                ('address', models.CharField(max_length=1024)),
                ('latitude', models.DecimalField(max_digits=10, decimal_places=7)),
                ('longitude', models.DecimalField(max_digits=10, decimal_places=7)),
                ('logo', models.FileField(help_text=b'Logo of Workshop', storage=services.s3.storage.S3Storage(), null=True, upload_to=core.models.common.content_file_name, blank=True)),
                ('open_at', models.TimeField(null=True, blank=True)),
                ('close_at', models.TimeField(null=True, blank=True)),
                ('off_days', multiselectfield.db.fields.MultiSelectField(blank=True, max_length=13, null=True, choices=[(1, b'Sunday'), (2, b'Monday'), (3, b'Tuesday'), (4, b'Wednesday'), (5, b'Thursday'), (6, b'Friday'), (7, b'Saturday')])),
                ('active', models.BooleanField(default=True)),
                ('city', models.ForeignKey(to='core.City')),
                ('vendor', models.ForeignKey(to='core.Vendor')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorkshopHoliday',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateField()),
                ('active', models.BooleanField(default=True)),
                ('workshop', models.ForeignKey(to='core.Workshop')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='actual_drop_address',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='actual_pickup_address',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='city',
            field=models.ForeignKey(default=1, to='core.City'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='carpanel',
            name='photo',
            field=models.FileField(default='/tmp/none.jpg', help_text=b'Panel of the car', storage=services.s3.storage.S3Storage(), upload_to=core.models.common.content_file_name),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='booking',
            name='sub_status',
            field=models.ForeignKey(to='core.BookingSubStatus', null=True),
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='car_panel',
            field=models.ForeignKey(to='core.CarPanel'),
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='city',
            field=models.ForeignKey(to='core.City'),
        ),
        migrations.AddField(
            model_name='carmodelpanel',
            name='car_panel',
            field=models.ForeignKey(to='core.CarPanel'),
        ),
        migrations.AddField(
            model_name='bookingpackagepanels',
            name='panel',
            field=models.ForeignKey(to='core.CarPanel'),
        ),
        migrations.AddField(
            model_name='booking',
            name='drop_address',
            field=models.ForeignKey(related_name='booking_drop_address', to='core.UserAddress', null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='pickup_address',
            field=models.ForeignKey(related_name='booking_pickup_address', to='core.UserAddress', null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='workshop',
            field=models.ForeignKey(default=1, to='core.Workshop'),
            preserve_default=False,
        ),
    ]
