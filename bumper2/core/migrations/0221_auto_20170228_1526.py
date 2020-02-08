# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0220_auto_20170228_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='incentiveevent',
            name='notifications',
            field=models.ManyToManyField(to='core.Notifications'),
        ),
        migrations.AlterField(
            model_name='historicalscratchfinderlead',
            name='phone',
            field=models.CharField(max_length=15, db_index=True),
        ),
        migrations.AlterField(
            model_name='scratchfinderlead',
            name='phone',
            field=models.CharField(unique=True, max_length=15, db_index=True),
        ),
    ]
