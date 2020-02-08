# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0106_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinginvoice',
            options={'ordering': ['-id']},
        ),
        migrations.RenameField(
            model_name='bookingdiscount',
            old_name='discount',
            new_name='labour_discount',
        ),
        migrations.AlterField(
            model_name='booking',
            name='source',
            field=models.CharField(blank=True, max_length=8, null=True, choices=[(b'web', b'Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'android', b'android'), (b'iphone', b'iphone')]),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='source',
            field=models.CharField(blank=True, max_length=8, null=True, choices=[(b'web', b'Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'android', b'android'), (b'iphone', b'iphone')]),
        ),
    ]
