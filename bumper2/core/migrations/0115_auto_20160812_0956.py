# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0114_remove_userinquiry_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinquiry',
            name='car_model',
            field=models.ForeignKey(blank=True, to='core.CarModel', null=True),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='name',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='phone',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='source',
            field=models.CharField(default=b'app', max_length=8, choices=[(b'web', b'Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone')]),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, b'Open'), (1, b'Postponed'), (1, b'Following Up'), (1, b'Closed - Booking created'), (1, b'RNR'), (1, b'Closed - Booking not created'), (1, b'Delayed Ops')]),
        ),
    ]
