# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0155_auto_20161108_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Hot'), (2, b'Warm'), (3, b'Cold'), (4, b'Red Hot')]),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='type_of_work',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Remove Scratches'), (2, b'Remove Dents and Scratches'), (3, b'Replace'), (4, b'Paint Only'), (5, b'Crumpled panel'), (6, b'Rusted Panel'), (7, b'Tear'), (8, b'Cleaning'), (9, b'Replace')]),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Hot'), (2, b'Warm'), (3, b'Cold'), (4, b'Red Hot')]),
        ),
        migrations.AlterField(
            model_name='historicaluserinquiry',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Hot'), (2, b'Warm'), (3, b'Cold'), (4, b'Red Hot')]),
        ),
        migrations.AlterField(
            model_name='userinquiry',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Hot'), (2, b'Warm'), (3, b'Cold'), (4, b'Red Hot')]),
        ),
    ]
