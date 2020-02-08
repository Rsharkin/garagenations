# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0218_auto_20170227_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalscratchfinderlead',
            name='detail',
            field=models.CharField(max_length=2048, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='scratchfinderlead',
            name='detail',
            field=models.CharField(max_length=2048, null=True, blank=True),
        ),
    ]
