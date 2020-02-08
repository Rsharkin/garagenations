# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0138_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='latitude',
            field=models.DecimalField(null=True, max_digits=9, decimal_places=6, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='longitude',
            field=models.DecimalField(null=True, max_digits=9, decimal_places=6, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='latitude',
            field=models.DecimalField(null=True, max_digits=9, decimal_places=6, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='longitude',
            field=models.DecimalField(null=True, max_digits=9, decimal_places=6, blank=True),
        ),
    ]
