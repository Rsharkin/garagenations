# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_bookingpackage_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarModelPanelPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('issue_type', models.PositiveSmallIntegerField(choices=[(1, b'Scratch'), (2, b'Dent'), (3, b'Replace'), (4, b'Paint Only')])),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CarTypePanelPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('car_type', models.PositiveSmallIntegerField(choices=[(1, b'Hatchback'), (2, b'Sedan'), (3, b'SUV'), (4, b'Luxury')])),
                ('issue_type', models.PositiveSmallIntegerField(choices=[(1, b'Scratch'), (2, b'Dent'), (3, b'Replace'), (4, b'Paint Only')])),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('active', models.BooleanField(default=True)),
                ('car_panel', models.ForeignKey(to='core.CarPanel')),
                ('city', models.ForeignKey(to='core.City')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='carmodelpanel',
            name='car_model',
        ),
        migrations.RemoveField(
            model_name='carmodelpanel',
            name='car_panel',
        ),
        migrations.RemoveField(
            model_name='carpanelprice',
            name='car_panel',
        ),
        migrations.RemoveField(
            model_name='carpanelprice',
            name='city',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanels',
            name='dent_type',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanels',
            name='panel',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanels',
            name='repair_or_replace',
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='price',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanels',
            name='price',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='carmodel',
            name='popular',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='CarModelPanel',
        ),
        migrations.DeleteModel(
            name='CarPanelPrice',
        ),
        migrations.AddField(
            model_name='carmodelpanelprice',
            name='car_model',
            field=models.ForeignKey(to='core.CarModel'),
        ),
        migrations.AddField(
            model_name='carmodelpanelprice',
            name='car_panel',
            field=models.ForeignKey(to='core.CarPanel'),
        ),
        migrations.AddField(
            model_name='carmodelpanelprice',
            name='city',
            field=models.ForeignKey(to='core.City'),
        ),
        migrations.AddField(
            model_name='bookingpackagepanels',
            name='modelprice',
            field=models.ForeignKey(to='core.CarModelPanelPrice', null=True),
        ),
        migrations.AddField(
            model_name='bookingpackagepanels',
            name='typeprice',
            field=models.ForeignKey(to='core.CarTypePanelPrice', null=True),
        ),
    ]
