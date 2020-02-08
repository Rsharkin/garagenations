# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpayment',
            name='payment_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Pay Now'), (2, b'Cash on Delivery')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Pay Now'), (2, b'Cash on Delivery')]),
        ),
    ]
