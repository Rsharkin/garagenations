# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0200_auto_20170201_2305'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookinghandoveritem',
            name='is_applicable',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='bookinghandoveritem',
            name='issue_reason',
            field=models.TextField(null=True, blank=True),
        ),
    ]
