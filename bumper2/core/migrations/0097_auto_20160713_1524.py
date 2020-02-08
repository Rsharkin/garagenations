# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0096_auto_20160713_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='action',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (101, 101), (102, 102), (103, 103), (104, 104), (105, 105), (106, 106), (51, 51)]),
        ),
        migrations.AddField(
            model_name='messages',
            name='notification',
            field=models.ForeignKey(blank=True, to='core.Notifications', null=True),
        ),
        migrations.AddField(
            model_name='messages',
            name='sent_by',
            field=models.ForeignKey(related_name='message_sent_by', blank=True, to=settings.AUTH_USER_MODEL, help_text=b'This is reference to user how has triggered the notification or sent the notification.', null=True),
        ),
    ]
