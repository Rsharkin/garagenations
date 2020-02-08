# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0241_auto_20170421_1228'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalReferralCampaign',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name', db_index=True)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('flow', models.CharField(help_text='Do not change this after creation. It is used in code', max_length=32, verbose_name='Flow')),
                ('referrer_credit', models.IntegerField(help_text='This will be given to user who is referring.', null=True, verbose_name='Referrer Credit', blank=True)),
                ('referred_credit', models.IntegerField(help_text='This will be given to user who got referred.', null=True, verbose_name='Referred Credit', blank=True)),
                ('referrer_tp_cash', models.IntegerField(help_text='This will be given to user who is referring.', null=True, verbose_name='Referrer Paytm Cash', blank=True)),
                ('referred_tp_cash', models.IntegerField(help_text='This will be given to user who got referred.', null=True, verbose_name='Referred Paytm Cash', blank=True)),
                ('active', models.BooleanField(default=False)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical Referral Campaign',
            },
        ),
        migrations.AddField(
            model_name='referralcampaign',
            name='notifications',
            field=models.ManyToManyField(to='core.Notifications'),
        ),
    ]
