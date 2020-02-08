# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0219_auto_20170227_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalscratchfinderlead',
            name='media',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.Media', null=True),
        ),
        migrations.AddField(
            model_name='scratchfinderlead',
            name='media',
            field=models.ForeignKey(related_name='sflead_media', default=1, to='core.Media'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(128, 128), (1, 1), (2, 2), (3, 3), (4, 4), (133, 133), (6, 6), (129, 129), (8, 8), (9, 9), (10, 10), (132, 132), (12, 12), (130, 130), (142, 142), (15, 15), (141, 141), (145, 145), (146, 146), (131, 131), (20, 20), (21, 21), (22, 22), (151, 151), (152, 152), (153, 153), (26, 26), (154, 154), (5, 5), (18, 18), (134, 134), (135, 135), (136, 136), (51, 51), (52, 52), (53, 53), (54, 54), (137, 137), (23, 23), (7, 7), (58, 58), (59, 59), (138, 138), (19, 19), (139, 139), (25, 25), (140, 140), (106, 106), (55, 55), (13, 13), (56, 56), (14, 14), (24, 24), (216, 216), (143, 143), (17, 17), (16, 16), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (144, 144), (107, 107), (108, 108), (109, 109), (111, 111), (112, 112), (113, 113), (114, 114), (115, 115), (116, 116), (117, 117), (118, 118), (119, 119), (120, 120), (121, 121), (122, 122), (123, 123), (124, 124), (125, 125), (126, 126), (127, 127)]),
        ),
    ]
