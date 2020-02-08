# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0115_auto_20160812_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinquiry',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, b'Open'), (2, b'Postponed'), (3, b'Following Up'), (4, b'Closed - Booking created'), (5, b'RNR'), (6, b'Closed - Booking not created'), (7, b'Delayed Ops')]),
        ),
    ]
