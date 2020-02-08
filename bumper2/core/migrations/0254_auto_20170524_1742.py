# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0253_auto_20170524_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaluserinquiry',
            name='city',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.City', null=True),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='city',
            field=models.ForeignKey(default=1, to='core.City'),
            preserve_default=False,
        ),
    ]
