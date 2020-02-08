# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingalerttriggerstatus',
            name='trigger',
            field=models.SmallIntegerField(choices=[(1, b'PICKUP_IN_1_HR'), (2, b'DROP_IN_6_HR'), (3, b'WORK_NOT_COMPLETE_DROP_IN_1_HR')]),
        ),
    ]
