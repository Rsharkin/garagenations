# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0127_auto_20160825_2130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalpayment',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='booking',
        ),
    ]
