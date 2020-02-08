# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0161_entitychangetracker'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='notice_for',
            field=models.CharField(default=b'flow', max_length=4, choices=[(b'flow', b'Flow'), (b'eod', b'EOD')]),
        ),
    ]
