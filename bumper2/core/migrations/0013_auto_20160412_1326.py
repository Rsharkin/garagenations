# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20160412_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingpackage',
            name='booking',
            field=models.ForeignKey(related_name='booking_package', to='core.Booking'),
        ),
    ]
