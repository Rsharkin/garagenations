# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0182_auto_20170106_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpayment',
            name='mode',
            field=models.SmallIntegerField(default=2, choices=[(1, b'Cash'), (2, b'Online'), (3, b'Email Invoice'), (4, b'SMS Link'), (5, b'Cheque'), (6, b'POS'), (7, b'Bank Transfer')]),
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(128, 128), (1, 1), (2, 2), (3, 3), (4, 4), (133, 133), (6, 6), (129, 129), (8, 8), (9, 9), (10, 10), (132, 132), (12, 12), (130, 130), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (131, 131), (20, 20), (21, 21), (22, 22), (151, 151), (152, 152), (153, 153), (26, 26), (154, 154), (5, 5), (134, 134), (135, 135), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (23, 23), (7, 7), (58, 58), (19, 19), (25, 25), (13, 13), (56, 56), (24, 24), (216, 216), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (107, 107), (108, 108), (109, 109), (111, 111), (112, 112), (113, 113), (114, 114), (115, 115), (116, 116), (117, 117), (118, 118), (119, 119), (120, 120), (121, 121), (122, 122), (123, 123), (124, 124), (125, 125), (126, 126), (127, 127)]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='mode',
            field=models.SmallIntegerField(default=2, choices=[(1, b'Cash'), (2, b'Online'), (3, b'Email Invoice'), (4, b'SMS Link'), (5, b'Cheque'), (6, b'POS'), (7, b'Bank Transfer')]),
        ),
    ]
