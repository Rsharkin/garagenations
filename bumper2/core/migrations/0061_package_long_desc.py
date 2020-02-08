# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0060_auto_20160518_2205'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='long_desc',
            field=models.CharField(max_length=2048, null=True, blank=True),
        ),
    ]
