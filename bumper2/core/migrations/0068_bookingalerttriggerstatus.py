# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_auto_20160527_0114'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingAlertTriggerStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('trigger', models.SmallIntegerField(choices=[(1, b'PICKUP_IN_1_HR')])),
                ('is_triggered', models.BooleanField(default=True, help_text=b'if already triggered then value will be true.')),
                ('booking', models.ForeignKey(related_name='bookingTrigger', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
