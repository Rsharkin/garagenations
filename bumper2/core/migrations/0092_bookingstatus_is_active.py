# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0091_auto_20160708_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingstatus',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
