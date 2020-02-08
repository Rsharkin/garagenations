# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0091_auto_20160708_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bumperuser',
            name='source',
            field=models.CharField(blank=True, max_length=8, null=True, choices=[(b'web', b'Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel')]),
        ),
    ]
