# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0245_auto_20170427_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreferralcampaign',
            name='terms',
            field=models.TextField(default='test', help_text='This will be shown to user', verbose_name='Terms And Conditions'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='referralcampaign',
            name='terms',
            field=models.TextField(default='test', help_text='This will be shown to user', verbose_name='Terms And Conditions'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='historicalreferralcampaign',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='referralcampaign',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='referralcampaign',
            name='notifications',
            field=models.ManyToManyField(to='core.Notifications', blank=True),
        ),
    ]
