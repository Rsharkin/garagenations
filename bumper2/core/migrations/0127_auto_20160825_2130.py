# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0126_userinquiry_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinquiry',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone')]),
        ),
    ]
