# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0194_auto_20170131_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entitychangetracker',
            name='content_id',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='entitychangetracker',
            name='item_tracked',
            field=models.CharField(help_text=b'Column name if tracking a column otherwise action', max_length=64, db_index=True),
        ),
    ]
