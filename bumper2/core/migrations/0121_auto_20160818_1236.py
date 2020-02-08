# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0120_auto_20160817_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdevices',
            name='device_type',
            field=models.CharField(blank=True, max_length=7, null=True, choices=[(b'android', b'android'), (b'ios', b'ios'), (b'web', b'web')]),
        ),
    ]
