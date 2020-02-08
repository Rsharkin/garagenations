# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0100_userinquiry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (107, 107), (51, 51)]),
        ),
        migrations.AlterField(
            model_name='package',
            name='category',
            field=models.PositiveSmallIntegerField(choices=[(1, b'VAS'), (2, b'Denting'), (3, b'Full Body Paint')]),
        ),
    ]
