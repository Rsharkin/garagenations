# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0246_auto_20170502_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalreferralcampaign',
            name='share_message',
            field=models.TextField(default='test', help_text='This message will be sent while sharing.', verbose_name='Share Message'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='referralcampaign',
            name='share_message',
            field=models.TextField(default='test', help_text='This message will be sent while sharing.', verbose_name='Share Message'),
            preserve_default=False,
        ),
    ]
