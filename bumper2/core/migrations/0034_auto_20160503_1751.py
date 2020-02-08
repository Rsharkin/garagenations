# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billitem',
            name='service_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='billitem',
            name='vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='bookingbill',
            name='discount',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
    ]
