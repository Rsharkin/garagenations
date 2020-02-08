# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0196_auto_20170131_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamalert',
            name='resolved',
            field=models.BooleanField(default=False),
        ),
    ]
