# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0134_auto_20160921_1238'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carpanelprice',
            name='dealer_price',
        ),
        migrations.AddField(
            model_name='carmodel',
            name='show_savings',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='carpanel',
            name='show_savings',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='dealer_labour_price',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='dealer_material_price',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='dealer_part_price',
            field=models.DecimalField(help_text=b'Inclusive of Tax', null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='carpanelprice',
            name='show_savings',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='booking',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'justdial', b'JustDial'), (b'opsPanel', b'OpsPanel')]),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'justdial', b'JustDial'), (b'opsPanel', b'OpsPanel')]),
        ),
    ]
