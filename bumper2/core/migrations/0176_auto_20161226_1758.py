# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0175_workshopuser'),
    ]

    operations = [
        migrations.RenameModel('BookingJobcard', 'BookingImage'),
        migrations.RenameModel('HistoricalBookingJobcard', 'HistoricalBookingImage')
    ]
