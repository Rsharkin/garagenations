# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0186_auto_20170120_1707'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userattendance',
            name='track_date',
        ),
        migrations.AddField(
            model_name='userattendance',
            name='track_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 20, 11, 44, 33, 201998, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
