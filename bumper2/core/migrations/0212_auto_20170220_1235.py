# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0211_auto_20170214_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='return_wo_work',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='return_wo_work',
            field=models.BooleanField(default=False),
        ),
    ]
