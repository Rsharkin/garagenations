# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_package_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='source',
            field=models.CharField(blank=True, max_length=5, null=True, choices=[(b'web', b'Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber')]),
        ),
        migrations.AlterField(
            model_name='userdevices',
            name='device_type',
            field=models.CharField(default=b'android', max_length=7, choices=[(b'android', b'android'), (b'ios', b'ios'), (b'web', b'web')]),
        ),
    ]
