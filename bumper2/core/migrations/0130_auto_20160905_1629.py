# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0129_auto_20160831_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='carpanelprice',
            name='dealer_price',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='packageprice',
            name='dealer_price',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Hot'), (2, b'Warm'), (3, b'Cold')]),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Hot'), (2, b'Warm'), (3, b'Cold')]),
        ),
        migrations.AlterField(
            model_name='historicaluserinquiry',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Hot'), (2, b'Warm'), (3, b'Cold')]),
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (107, 107), (108, 108), (109, 109), (51, 51), (52, 52)]),
        ),
        migrations.AlterField(
            model_name='userinquiry',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Hot'), (2, b'Warm'), (3, b'Cold')]),
        ),
    ]
