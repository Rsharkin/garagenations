# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0193_auto_20170130_1620'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookingchangelog',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='bookingchangelog',
            name='delay_reason',
        ),
        migrations.RemoveField(
            model_name='bookingchangelog',
            name='updated_by',
        ),
        migrations.AddField(
            model_name='entitychangetracker',
            name='delay_reason',
            field=models.ForeignKey(related_name='bc_delay_reason', blank=True, to='core.DelayReasons', null=True),
        ),
        migrations.AddField(
            model_name='entitychangetracker',
            name='reason_text',
            field=models.TextField(default=b'No Reason'),
        ),
        migrations.AddField(
            model_name='entitychangetracker',
            name='updated_by',
            field=models.ForeignKey(related_name='bc_udpated_by', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='BookingChangeLog',
        ),
    ]
