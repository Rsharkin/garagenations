# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0098_auto_20160714_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='carpanel',
            name='part_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Panel'), (2, b'Spare Part')]),
        ),
    ]
