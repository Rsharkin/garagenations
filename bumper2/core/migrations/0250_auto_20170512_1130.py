# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0249_auto_20170508_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='kk_tax',
            field=models.DecimalField(default=0.5, help_text=b'Krishi Kalyan in percentage', max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='sb_tax',
            field=models.DecimalField(default=0.5, help_text=b'Swacch Bharat tax in percentage', max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='service_tax',
            field=models.DecimalField(default=14, help_text=b'Base service tax in percentage', max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='city',
            name='vat',
            field=models.DecimalField(default=14.5, help_text=b'VAT in percentage', max_digits=10, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='historicalreferralcampaign',
            name='share_message',
            field=models.TextField(help_text='This message will be sent while sharing. Use {%referral_code%} to include referral code', verbose_name='Share Message'),
        ),
        migrations.AlterField(
            model_name='historicalreferralcampaign',
            name='share_title',
            field=models.TextField(help_text='This title will be sent while sharing. Use {%referral_code%} to include referral code', verbose_name='Share Title'),
        ),
        migrations.AlterField(
            model_name='referralcampaign',
            name='share_message',
            field=models.TextField(help_text='This message will be sent while sharing. Use {%referral_code%} to include referral code', verbose_name='Share Message'),
        ),
        migrations.AlterField(
            model_name='referralcampaign',
            name='share_title',
            field=models.TextField(help_text='This title will be sent while sharing. Use {%referral_code%} to include referral code', verbose_name='Share Title'),
        ),
    ]
