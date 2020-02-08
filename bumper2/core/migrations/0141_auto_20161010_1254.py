# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0140_auto_20161006_1444'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpayment',
            name='device_type',
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='device_type',
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
    ]
