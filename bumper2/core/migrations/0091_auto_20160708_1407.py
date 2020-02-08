# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0090_auto_20160707_1804'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partnerlead',
            old_name='utm_mode',
            new_name='utm_medium',
        ),
        migrations.AlterField(
            model_name='bumperuser',
            name='source',
            field=models.CharField(blank=True, max_length=5, null=True, choices=[(b'web', b'Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel')]),
        ),
    ]
