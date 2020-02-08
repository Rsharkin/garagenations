# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20160419_1339'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingPackagePanel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('booking_package', models.ForeignKey(to='core.BookingPackage')),
                ('modelprice', models.ForeignKey(to='core.CarModelPanelPrice', null=True)),
                ('typeprice', models.ForeignKey(to='core.CarTypePanelPrice', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanels',
            name='booking_package',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanels',
            name='modelprice',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanels',
            name='typeprice',
        ),
        migrations.DeleteModel(
            name='BookingPackagePanels',
        ),
    ]
