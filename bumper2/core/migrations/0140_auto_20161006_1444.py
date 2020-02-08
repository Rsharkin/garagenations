# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0139_auto_20160928_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='latitude',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=8, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='longitude',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=8, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='latitude',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=8, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='longitude',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=8, blank=True),
        ),
    ]
