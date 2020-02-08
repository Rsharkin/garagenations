# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0225_auto_20170313_1826'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicaluservendorcash',
            old_name='detail',
            new_name='promise_info',
        ),
        migrations.RenameField(
            model_name='uservendorcash',
            old_name='detail',
            new_name='promise_info',
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='settle_info',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='transfer_info',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='tx_data',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='uservendorcash',
            name='settle_info',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='uservendorcash',
            name='transfer_info',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='uservendorcash',
            name='tx_data',
            field=models.TextField(null=True, blank=True),
        ),
    ]
