# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0130_auto_20160905_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowupTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='booking',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'justdial', b'JustDial')]),
        ),
        migrations.AlterField(
            model_name='bumperuser',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'helpshift', b'Helpshift'), (b'justdial', b'JustDial')]),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'justdial', b'JustDial')]),
        ),
        migrations.AlterField(
            model_name='historicaluserinquiry',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'helpshift', b'Helpshift'), (b'justdial', b'JustDial')]),
        ),
        migrations.AlterField(
            model_name='userinquiry',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'helpshift', b'Helpshift'), (b'justdial', b'JustDial')]),
        ),
        migrations.AddField(
            model_name='followup',
            name='tags',
            field=models.ManyToManyField(to='core.FollowupTag', blank=True),
        ),
    ]
