# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0144_auto_20161019_1818'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookingalerttriggerstatus',
            name='trigger',
        ),
        migrations.RemoveField(
            model_name='opsalerttype',
            name='cancel_action',
        ),
        migrations.RemoveField(
            model_name='opsalerttype',
            name='create_action',
        ),
        migrations.AddField(
            model_name='bookingalerttriggerstatus',
            name='alert_type',
            field=models.ForeignKey(blank=True, to='core.OpsAlertType', null=True),
        ),
        migrations.AddField(
            model_name='opsalerttype',
            name='exclude_conditions',
            field=models.CharField(help_text=b'Django Query Conditions for excluding the bookings', max_length=1024, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='opsalerttype',
            name='filter_conditions',
            field=models.CharField(default={}, help_text=b'Static Django Query Conditions for filtering the bookings', max_length=1024),
            preserve_default=False,
        ),
    ]
