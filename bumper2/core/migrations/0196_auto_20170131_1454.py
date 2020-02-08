# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0195_auto_20170131_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamAlert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reason_text', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'TeamAlert',
            },
        ),
        migrations.CreateModel(
            name='TeamAlertReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('reason_type', models.PositiveSmallIntegerField(choices=[(1, b'Raised by workshop team'), (2, b'Raised by Crew team')])),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='teamalert',
            name='alert_reason',
            field=models.ForeignKey(related_name='ta_alert_reason', to='core.TeamAlertReason'),
        ),
        migrations.AddField(
            model_name='teamalert',
            name='updated_by',
            field=models.ForeignKey(related_name='ta_udpated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='teamalert',
            name='workshop',
            field=models.ForeignKey(blank=True, to='core.Workshop', null=True),
        ),
    ]
