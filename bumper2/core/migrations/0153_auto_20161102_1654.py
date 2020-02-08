# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0152_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='push_level',
            field=models.SmallIntegerField(default=1, null=True, blank=True, choices=[(1, b'Status'), (2, b'Feedback'), (3, b'Update'), (4, b'Offer'), (5, b'Referral')]),
        ),
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (23, 23), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (216, 216), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (151, 151), (152, 152), (153, 153), (26, 26), (24, 24), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (17, 17), (107, 107), (108, 108), (109, 109), (111, 111), (51, 51), (25, 25), (53, 53), (52, 52), (106, 106)]),
        ),
    ]
