# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20160430_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='drop_address',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='pickup_address',
        ),
        migrations.RemoveField(
            model_name='historicalbooking',
            name='drop_address',
        ),
        migrations.RemoveField(
            model_name='historicalbooking',
            name='pickup_address',
        ),
    ]
