# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0280_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingopsstatus',
            name='show_to_cust',
            field=models.BooleanField(default=False),
        ),
    ]
