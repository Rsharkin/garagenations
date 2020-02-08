# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0118_auto_20160812_1125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='followup',
            name='booking',
        ),
    ]
