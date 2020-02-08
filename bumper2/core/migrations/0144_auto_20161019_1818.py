# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0143_auto_20161018_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='opsalerttype',
            name='cancel_action',
            field=models.IntegerField(default=1, help_text=b'action to be taken to cancel this alert.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='opsalerttype',
            name='create_action',
            field=models.IntegerField(default=1, help_text=b'action to be taken for alert to be created.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='opsalerttype',
            name='notification',
            field=models.ForeignKey(default=1, to='core.Notifications'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='opsalerttype',
            name='time_field',
            field=models.CharField(help_text=b'this is the field in booking table with which the time diff will be calculated. If this is empty, then current time will be used.', max_length=128, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='bookingopsalerts',
            name='alert_status',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Pending'), (2, b'Sent'), (3, b'Cancelled')]),
        ),
        migrations.AlterField(
            model_name='opsalerttype',
            name='time_diff',
            field=models.IntegerField(help_text=b'in minutes'),
        ),
    ]
