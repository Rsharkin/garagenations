# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20160429_1409'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingPackagePanel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('booking_package', models.ForeignKey(related_name='booking_package_panel', to='core.BookingPackage')),
                ('panel', models.ForeignKey(to='core.CarPanelPrice', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel1',
            name='booking_package',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel1',
            name='panel',
        ),
        migrations.DeleteModel(
            name='BookingPackagePanel1',
        ),
    ]
