# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0247_auto_20170504_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreferralcampaign',
            name='share_title',
            field=models.TextField(default='test', help_text='This title will be sent while sharing.', verbose_name='Share Title'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='referralcampaign',
            name='share_title',
            field=models.TextField(default='test', help_text='This title will be sent while sharing.', verbose_name='Share Title'),
            preserve_default=False,
        ),
    ]
