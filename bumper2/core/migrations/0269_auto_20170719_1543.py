# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0268_auto_20170719_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carcolor',
            name='color_code',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='carcolor',
            name='color_name',
            field=models.CharField(unique=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='credittransaction',
            name='entity',
            field=models.CharField(blank=True, max_length=64, null=True, db_index=True, choices=[(b'Booking', b'Booking'), (b'Referral', b'Referral'), (b'BumperUser', b'BumperUser')]),
        ),
    ]
