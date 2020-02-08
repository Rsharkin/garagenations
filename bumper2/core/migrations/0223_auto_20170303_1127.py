# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0222_auto_20170302_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalscratchfinderlead',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, b'Submitted'), (2, b'Approved'), (3, b'Rejected')]),
        ),
        migrations.AlterField(
            model_name='incentiveevent',
            name='notifications',
            field=models.ManyToManyField(to='core.Notifications', blank=True),
        ),
        migrations.AlterField(
            model_name='scratchfinderlead',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, b'Submitted'), (2, b'Approved'), (3, b'Rejected')]),
        ),
    ]
