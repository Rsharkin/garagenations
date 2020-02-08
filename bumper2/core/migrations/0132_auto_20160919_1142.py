# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0131_auto_20160912_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpayment',
            name='payment_type',
            field=models.PositiveSmallIntegerField(default=2, choices=[(1, b'Pay Now'), (2, b'Cash on Delivery')]),
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (216, 216), (25, 25), (26, 26), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (107, 107), (108, 108), (109, 109), (24, 24), (51, 51), (52, 52)]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.PositiveSmallIntegerField(default=2, choices=[(1, b'Pay Now'), (2, b'Cash on Delivery')]),
        ),
    ]
