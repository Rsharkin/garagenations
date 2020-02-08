# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0063_auto_20160519_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='carpanel',
            name='sort_order',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='package',
            name='sort_order',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
