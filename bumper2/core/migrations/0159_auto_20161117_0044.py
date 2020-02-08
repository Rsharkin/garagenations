# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0158_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingfeedback',
            name='customer_relation_remarks',
            field=models.CharField(max_length=2048, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='type_of_work',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Remove Scratches'), (2, b'Remove Dents and Scratches'), (3, b'Replace'), (4, b'Paint Only'), (5, b'Crumpled panel'), (6, b'Rusted Panel'), (7, b'Tear'), (8, b'Cleaning'), (9, b'Replace with FBB')]),
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (51, 51), (52, 52), (53, 53), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (107, 107), (108, 108), (109, 109), (111, 111), (112, 112), (113, 113), (114, 114), (115, 115), (116, 116), (117, 117), (118, 118), (119, 119), (120, 120), (121, 121), (122, 122), (123, 123), (151, 151), (152, 152), (153, 153), (216, 216)]),
        ),
    ]
