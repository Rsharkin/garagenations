# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0229_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Referral',
                'verbose_name_plural': 'Referrals',
            },
        ),
        migrations.CreateModel(
            name='ReferralCampaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('flow', models.CharField(help_text='Do not change this after creation. It is used in code', max_length=32, verbose_name='Flow', choices=[(b'CREATE_USER', b'Create User flow')])),
                ('referrer_credit', models.IntegerField(help_text='This will be given to user who is referring.', null=True, verbose_name='Referrer Credit', blank=True)),
                ('referred_credit', models.IntegerField(help_text='This will be given to user who got referred.', null=True, verbose_name='Referred Credit', blank=True)),
                ('referrer_tp_cash', models.IntegerField(help_text='This will be given to user who is referring.', null=True, verbose_name='Referrer Paytm Cash', blank=True)),
                ('referred_tp_cash', models.IntegerField(help_text='This will be given to user who got referred.', null=True, verbose_name='Referred Paytm Cash', blank=True)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Referral Campaign',
                'verbose_name_plural': 'Referral Campaigns',
            },
        ),
        migrations.CreateModel(
            name='ReferralCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('code', models.CharField(help_text='Leaving this field empty will generate a random code.', unique=True, max_length=30, verbose_name='Code')),
                ('active', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(verbose_name='Referral Campaign', to='core.ReferralCampaign')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
                'verbose_name': 'ReferralCode',
                'verbose_name_plural': 'Referral Codes',
            },
        ),
        migrations.AlterField(
            model_name='notifications',
            name='is_promo',
            field=models.BooleanField(default=False, help_text=b'You want to send a promotional SMS?'),
        ),
        migrations.AlterField(
            model_name='notifications',
            name='send_notice_to',
            field=models.SmallIntegerField(default=2, choices=[(1, b'Customer'), (2, b'Ops'), (3, b'Pickup Driver'), (4, b'Drop Driver'), (5, b'Workshop Executive'), (6, b'Custom Number/Email')]),
        ),
        migrations.AddField(
            model_name='referral',
            name='campaign',
            field=models.ForeignKey(to='core.ReferralCampaign'),
        ),
        migrations.AddField(
            model_name='referral',
            name='referred',
            field=models.ForeignKey(related_name='referreduser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='referral',
            name='referrer',
            field=models.ForeignKey(related_name='referreruser', to=settings.AUTH_USER_MODEL),
        ),
    ]
