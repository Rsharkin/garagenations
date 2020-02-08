# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0082_auto_20160616_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingdiscount',
            name='reason',
            field=models.CharField(default='old discount', max_length=2048),
            preserve_default=False,
        ),
    ]
