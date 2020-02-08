# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0221_auto_20170228_1526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicaluservendorcash',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='historicaluservendorcash',
            name='is_promised',
        ),
        migrations.RemoveField(
            model_name='incentiveevent',
            name='is_promised',
        ),
        migrations.RemoveField(
            model_name='uservendorcash',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='uservendorcash',
            name='is_promised',
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='cancelled',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='detail',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='entity',
            field=models.CharField(blank=True, max_length=64, null=True, choices=[(b'Booking', b'Booking'), (b'ScratchFinderLead', b'ScratchFinderLead')]),
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='entity_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='transferred',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AddField(
            model_name='uservendorcash',
            name='cancelled',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AddField(
            model_name='uservendorcash',
            name='detail',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='uservendorcash',
            name='entity',
            field=models.CharField(blank=True, max_length=64, null=True, choices=[(b'Booking', b'Booking'), (b'ScratchFinderLead', b'ScratchFinderLead')]),
        ),
        migrations.AddField(
            model_name='uservendorcash',
            name='entity_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='uservendorcash',
            name='transferred',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='historicaluservendorcash',
            name='settled',
            field=models.BooleanField(default=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='incentiveevent',
            name='credit',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='incentiveevent',
            name='tp',
            field=models.PositiveSmallIntegerField(blank=True, help_text=b'Third Party Name', null=True, choices=[(1, b'PayTM')]),
        ),
        migrations.AlterField(
            model_name='incentiveevent',
            name='tp_cash',
            field=models.DecimalField(help_text=b'Third Party Cash Amount', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='uservendorcash',
            name='settled',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
