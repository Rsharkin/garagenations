# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0216_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userdevices',
            old_name='is_dev',
            new_name='is_fcm',
        ),
        migrations.RemoveField(
            model_name='notifications',
            name='only_for_user',
        ),
        migrations.AddField(
            model_name='userdevices',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='userdevices',
            name='device_id',
            field=models.CharField(help_text=b'This stores gcm id or apns or fcm ID and is used as alternate to device id to uniquely identify device', max_length=512, null=True),
        ),
    ]
