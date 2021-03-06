# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0172_auto_20161213_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='final_cancel_reason',
            field=models.ForeignKey(related_name='booking_final_cancel_reason', blank=True, to='core.CancellationReasons', null=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='final_cancel_reason',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.CancellationReasons', null=True),
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (107, 107), (108, 108), (109, 109), (111, 111), (112, 112), (113, 113), (114, 114), (115, 115), (116, 116), (117, 117), (118, 118), (119, 119), (120, 120), (121, 121), (122, 122), (123, 123), (124, 124), (125, 125), (126, 126), (127, 127), (151, 151), (152, 152), (153, 153), (216, 216)]),
        ),
    ]
