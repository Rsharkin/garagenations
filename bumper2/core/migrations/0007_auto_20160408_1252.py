# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_usercar'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingPackage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('estimate_price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('actual_price', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BookingStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=128)),
                ('status_desc', models.CharField(max_length=256)),
                ('flow_order_num', models.SmallIntegerField(default=1)),
            ],
            options={
                'ordering': ['flow_order_num'],
                'verbose_name_plural': 'Booking Statuses',
            },
        ),
        migrations.CreateModel(
            name='BookingSubStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sub_status', models.CharField(max_length=128)),
                ('sub_status_desc', models.CharField(max_length=256)),
                ('flow_order_num', models.SmallIntegerField(default=1)),
                ('status', models.ForeignKey(to='core.BookingStatus')),
            ],
            options={
                'ordering': ['status__flow_order_num', 'flow_order_num'],
                'verbose_name_plural': 'Booking Sub Statuses',
            },
        ),
        migrations.CreateModel(
            name='CancellationReasons',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(max_length=64)),
                ('reason_owner', models.PositiveSmallIntegerField(choices=[(1, b'Customer'), (2, b'Ops')])),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CarPanel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('desc', models.CharField(max_length=512)),
                ('active', models.BooleanField(default=True)),
                ('city', models.ForeignKey(to='core.City')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ItemPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('car_type', models.SmallIntegerField(choices=[(1, b'Hatchback'), (2, b'Sedan'), (3, b'SUV'), (4, b'Luxury')])),
                ('item', models.ForeignKey(to='core.Item')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('desc', models.CharField(max_length=512)),
                ('pickup_type', models.SmallIntegerField(choices=[(1, b'Bumper'), (2, b'Workshop'), (3, b'Self')])),
                ('is_doorstep', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('city', models.ForeignKey(to='core.City')),
                ('items', models.ManyToManyField(to='core.Item')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PackagePrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('car_type', models.SmallIntegerField(choices=[(1, b'Hatchback'), (2, b'Sedan'), (3, b'SUV'), (4, b'Luxury')])),
                ('package', models.ForeignKey(to='core.Package')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='usercar',
            field=models.ForeignKey(default=1, to='core.UserCar'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='booking',
            field=models.ForeignKey(to='core.Booking'),
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='package',
            field=models.ForeignKey(to='core.PackagePrice'),
        ),
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.ForeignKey(default=1, to='core.BookingStatus'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='sub_status',
            field=models.ForeignKey(default=1, to='core.BookingSubStatus'),
            preserve_default=False,
        ),
    ]
