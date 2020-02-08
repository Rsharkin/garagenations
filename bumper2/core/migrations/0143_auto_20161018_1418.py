# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0142_auto_20161013_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carmodel',
            name='car_type',
            field=models.SmallIntegerField(default=5, choices=[(1, b'Hatchback'), (2, b'Sedan'), (3, b'SUV'), (4, b'Luxury'), (5, b'Hatchback1'), (6, b'Hatchback2'), (7, b'Hatchback3'), (8, b'Sedan1'), (9, b'Sedan2'), (10, b'Sedan3'), (11, b'SUV1'), (12, b'SUV2'), (13, b'SUV3')]),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='car_type',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'Hatchback'), (2, b'Sedan'), (3, b'SUV'), (4, b'Luxury'), (5, b'Hatchback1'), (6, b'Hatchback2'), (7, b'Hatchback3'), (8, b'Sedan1'), (9, b'Sedan2'), (10, b'Sedan3'), (11, b'SUV1'), (12, b'SUV2'), (13, b'SUV3')]),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='type_of_work',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Remove Scratches'), (2, b'Remove Dents and Scratches'), (3, b'Replace'), (4, b'Paint Only'), (5, b'Crumpled panel'), (6, b'Rusted Panel'), (7, b'Tear'), (8, b'Cleaning')]),
        ),
        migrations.AlterField(
            model_name='itemprice',
            name='car_type',
            field=models.SmallIntegerField(choices=[(1, b'Hatchback'), (2, b'Sedan'), (3, b'SUV'), (4, b'Luxury'), (5, b'Hatchback1'), (6, b'Hatchback2'), (7, b'Hatchback3'), (8, b'Sedan1'), (9, b'Sedan2'), (10, b'Sedan3'), (11, b'SUV1'), (12, b'SUV2'), (13, b'SUV3')]),
        ),
        migrations.AlterField(
            model_name='packageprice',
            name='car_type',
            field=models.SmallIntegerField(choices=[(1, b'Hatchback'), (2, b'Sedan'), (3, b'SUV'), (4, b'Luxury'), (5, b'Hatchback1'), (6, b'Hatchback2'), (7, b'Hatchback3'), (8, b'Sedan1'), (9, b'Sedan2'), (10, b'Sedan3'), (11, b'SUV1'), (12, b'SUV2'), (13, b'SUV3')]),
        ),
    ]
