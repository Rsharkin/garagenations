# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0207_auto_20170210_1303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='filename',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
