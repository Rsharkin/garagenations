# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20160419_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingpackagepanel',
            name='booking_package',
            field=models.ForeignKey(related_name='booking_package_panel', to='core.BookingPackage'),
        ),
    ]
