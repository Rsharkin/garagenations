# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpayment',
            name='payment_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Pay Now'), (1, b'Pay on Delivery')]),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Pay Now'), (1, b'Pay on Delivery')]),
        ),
        migrations.AlterField(
            model_name='historicalpayment',
            name='tx_status',
            field=models.CharField(default=b'pending', max_length=7, choices=[(b'success', b'Success'), (b'failed', b'Failed'), (b'pending', b'Pending')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='tx_status',
            field=models.CharField(default=b'pending', max_length=7, choices=[(b'success', b'Success'), (b'failed', b'Failed'), (b'pending', b'Pending')]),
        ),
    ]
