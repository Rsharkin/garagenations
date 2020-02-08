# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0227_auto_20170316_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='is_promo',
            field=models.BooleanField(default=False, help_text=b'You want to send a promotional email?'),
        ),
    ]
