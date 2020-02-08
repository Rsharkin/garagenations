# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_auto_20160511_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpayment',
            name='tx_status',
            field=models.IntegerField(default=3, choices=[(1, b'Success'), (2, b'Failed'), (3, b'Pending')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='booking',
            field=models.ForeignKey(related_name='booking_payment', to='core.Booking'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='tx_status',
            field=models.IntegerField(default=3, choices=[(1, b'Success'), (2, b'Failed'), (3, b'Pending')]),
        ),
    ]
