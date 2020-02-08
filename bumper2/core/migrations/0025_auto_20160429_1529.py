# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20160429_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carpanelprice',
            name='car_model',
            field=models.ForeignKey(to='core.CarModel', null=True),
        ),
        migrations.AlterField(
            model_name='carpanelprice',
            name='car_type',
            field=models.PositiveSmallIntegerField(null=True, choices=[(1, b'Hatchback'), (2, b'Sedan'), (3, b'SUV'), (4, b'Luxury')]),
        ),
    ]
