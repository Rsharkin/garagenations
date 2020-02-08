# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0161_auto_20161122_1102'),
    ]

    operations = [
        migrations.CreateModel(
            name='InquiryCancellationReasons',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(max_length=64)),
                ('reason_owner', models.PositiveSmallIntegerField(choices=[(1, b'Customer'), (2, b'Ops')])),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='historicaluserinquiry',
            name='cancellation_reason',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.InquiryCancellationReasons', null=True),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='cancellation_reason',
            field=models.ForeignKey(blank=True, to='core.InquiryCancellationReasons', null=True),
        ),
    ]
