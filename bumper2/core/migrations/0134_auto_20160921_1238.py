# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0133_auto_20160920_0854'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpayment',
            name='merchant_trx_id',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='merchant_trx_id',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalpayment',
            name='tx_type',
            field=models.SmallIntegerField(default=1, choices=[(1, b'Payment'), (2, b'Refund'), (3, b'Void')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='tx_type',
            field=models.SmallIntegerField(default=1, choices=[(1, b'Payment'), (2, b'Refund'), (3, b'Void')]),
        ),
    ]
