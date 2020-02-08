# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0171_auto_20161208_2213'),
    ]

    operations = [
        migrations.CreateModel(
            name='DelayReasons',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='booking',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'justdial', b'JustDial'), (b'opsPanel', b'OpsPanel'), (b'drwheelz', b'drwheelz'), (b'incomingCall', b'Incoming Call'), (b'urbanClap', b'UrbanClap'), (b'rework', b'Rework')]),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'justdial', b'JustDial'), (b'opsPanel', b'OpsPanel'), (b'drwheelz', b'drwheelz'), (b'incomingCall', b'Incoming Call'), (b'urbanClap', b'UrbanClap'), (b'rework', b'Rework')]),
        ),
        migrations.AddField(
            model_name='booking',
            name='delay_reason',
            field=models.ForeignKey(related_name='booking_delay_reason', blank=True, to='core.DelayReasons', null=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='delay_reason',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.DelayReasons', null=True),
        ),
    ]
