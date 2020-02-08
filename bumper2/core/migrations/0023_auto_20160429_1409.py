# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20160425_1311'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingPackagePanel1',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('booking_package', models.ForeignKey(related_name='booking_package_panel1', to='core.BookingPackage')),
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
                ('type_of_work', models.PositiveSmallIntegerField(choices=[(1, b'Scratch'), (2, b'Dent'), (3, b'Replace'), (4, b'Paint Only')])),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('active', models.BooleanField(default=True)),
                ('car_model', models.ForeignKey(to='core.CarModel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='booking_package',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='modelprice',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='typeprice',
        ),
        migrations.RemoveField(
            model_name='carmodelpanelprice',
            name='car_model',
        ),
        migrations.RemoveField(
            model_name='carmodelpanelprice',
            name='car_panel',
        ),
        migrations.RemoveField(
            model_name='carmodelpanelprice',
            name='city',
        ),
        migrations.RemoveField(
            model_name='cartypepanelprice',
            name='car_panel',
        ),
        migrations.RemoveField(
            model_name='cartypepanelprice',
            name='city',
        ),
        migrations.AddField(
            model_name='carpanel',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.DeleteModel(
            name='BookingPackagePanel',
        ),
        migrations.DeleteModel(
            name='CarModelPanelPrice',
        ),
        migrations.DeleteModel(
            name='CarTypePanelPrice',
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='car_panel',
            field=models.ForeignKey(related_name='panel_price', to='core.CarPanel'),
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='city',
            field=models.ForeignKey(to='core.City'),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel1',
            name='panel',
            field=models.ForeignKey(to='core.CarPanelPrice', null=True),
        ),
    ]
