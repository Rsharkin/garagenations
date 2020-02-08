# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0189_auto_20170123_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingpackage',
            name='extra',
            field=models.BooleanField(default=False, help_text=b'Is this package extra after rework.'),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='extra',
            field=models.BooleanField(default=False, help_text=b'Is this panel extra after rework.'),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='extra',
            field=models.BooleanField(default=False, help_text=b'Is this package extra after rework.'),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='extra',
            field=models.BooleanField(default=False, help_text=b'Is this panel extra after rework.'),
        ),
        migrations.AlterField(
            model_name='bookingpackagepanel',
            name='rework',
            field=models.BooleanField(default=False, help_text=b'Rework done on this panel.'),
        ),
        migrations.AlterField(
            model_name='bookingqualitychecks',
            name='booking_image',
            field=models.ForeignKey(related_name='booking_qc_images', blank=True, to='core.BookingImage', null=True),
        ),
        migrations.AlterField(
            model_name='historicalbookingpackagepanel',
            name='rework',
            field=models.BooleanField(default=False, help_text=b'Rework done on this panel.'),
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(128, 128), (1, 1), (2, 2), (3, 3), (4, 4), (133, 133), (6, 6), (129, 129), (8, 8), (9, 9), (10, 10), (132, 132), (12, 12), (130, 130), (142, 142), (15, 15), (141, 141), (17, 17), (18, 18), (131, 131), (20, 20), (21, 21), (22, 22), (151, 151), (152, 152), (153, 153), (26, 26), (154, 154), (5, 5), (134, 134), (135, 135), (136, 136), (51, 51), (52, 52), (53, 53), (54, 54), (137, 137), (23, 23), (7, 7), (58, 58), (138, 138), (19, 19), (139, 139), (25, 25), (140, 140), (55, 55), (13, 13), (56, 56), (14, 14), (24, 24), (216, 216), (16, 16), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (107, 107), (108, 108), (109, 109), (111, 111), (112, 112), (113, 113), (114, 114), (115, 115), (116, 116), (117, 117), (118, 118), (119, 119), (120, 120), (121, 121), (122, 122), (123, 123), (124, 124), (125, 125), (126, 126), (127, 127)]),
        ),
        migrations.AlterField(
            model_name='package',
            name='category',
            field=models.PositiveSmallIntegerField(choices=[(1, b'VAS'), (2, b'Denting'), (3, b'Full Body Paint'), (4, b'Advance Payment To'), (5, b'Advance Payment From')]),
        ),
    ]
