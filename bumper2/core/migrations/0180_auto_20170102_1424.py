# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0179_auto_20170102_1334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bumperuser',
            name='source',
            field=models.ForeignKey(related_name='user_sources', db_column=b'source', blank=True, to='core.Source', null=True),
        ),
        migrations.AlterField(
            model_name='historicaluserinquiry',
            name='source',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'source', db_constraint=False, blank=True, to='core.Source', null=True),
        ),
        migrations.AlterField(
            model_name='userinquiry',
            name='source',
            field=models.ForeignKey(related_name='userinquiry_sources', db_column=b'source', blank=True, to='core.Source', null=True),
        ),
    ]
