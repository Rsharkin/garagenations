# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20160411_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='category',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'VAS'), (2, b'Denting')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='package',
            name='pickup_type',
            field=models.PositiveSmallIntegerField(choices=[(1, b'Bumper'), (2, b'Workshop'), (3, b'Self')]),
        ),
    ]
