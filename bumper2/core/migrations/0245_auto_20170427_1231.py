# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0244_auto_20170425_1249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalreferralcampaign',
            name='flow',
        ),
        migrations.RemoveField(
            model_name='referralcampaign',
            name='flow',
        ),
        migrations.AlterField(
            model_name='historicalreferralcampaign',
            name='name',
            field=models.CharField(help_text='Do not change this after creation. It is used in code', max_length=255, verbose_name='Name', db_index=True),
        ),
        migrations.AlterField(
            model_name='referral',
            name='referred',
            field=models.ForeignKey(related_name='referreduser', to=settings.AUTH_USER_MODEL, help_text=b'New user referred by existing'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='referrer',
            field=models.ForeignKey(related_name='referreruser', to=settings.AUTH_USER_MODEL, help_text=b'Existing user referred new user'),
        ),
        migrations.AlterField(
            model_name='referralcampaign',
            name='name',
            field=models.CharField(help_text='Do not change this after creation. It is used in code', unique=True, max_length=255, verbose_name='Name'),
        ),
    ]
