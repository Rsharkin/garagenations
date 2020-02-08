# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0168_auto_20161202_1925'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingReworkPackage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(help_text=b'Reason for rework', max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BookingReworkPackagePanel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type_of_work', models.PositiveSmallIntegerField(choices=[(1, b'Remove Scratches'), (2, b'Remove Dents and Scratches'), (3, b'Replace'), (4, b'Paint Only'), (5, b'Crumpled panel'), (6, b'Rusted Panel'), (7, b'Tear'), (8, b'Cleaning'), (9, b'Replace')])),
                ('reason', models.CharField(help_text=b'Reason for rework', max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='rework',
            field=models.BooleanField(default=False, help_text=b'Rework done on this package.'),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='rework',
            field=models.BooleanField(default=False, help_text=b'Rework done on this package.'),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='rework',
            field=models.BooleanField(default=False, help_text=b'Rework done on this package.'),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='rework',
            field=models.BooleanField(default=False, help_text=b'Rework done on this package.'),
        ),
        migrations.AddField(
            model_name='bookingreworkpackagepanel',
            name='booking_package_panel',
            field=models.ForeignKey(related_name='rework_panel', to='core.BookingPackagePanel'),
        ),
        migrations.AddField(
            model_name='bookingreworkpackage',
            name='booking_package',
            field=models.ForeignKey(related_name='rework_package', to='core.BookingPackage'),
        ),
    ]
