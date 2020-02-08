# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0270_auto_20170721_1142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookingpartdoc',
            name='final_price_cust',
        ),
        migrations.RemoveField(
            model_name='bookingpartquote',
            name='part_number',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpartdoc',
            name='final_price_cust',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpartquote',
            name='part_number',
        ),
        migrations.AddField(
            model_name='bookingpartdoc',
            name='part_number',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbookingpartdoc',
            name='part_number',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='followup',
            name='comm_mode',
            field=models.PositiveSmallIntegerField(default=1, help_text=b'How was the customer communicated?', choices=[(1, b'Call'), (2, b'WhatsApp'), (3, b'SMS'), (4, b'Email'), (5, b'Executive App'), (6, b'Push'), (7, b'Web Chat'), (8, b'Helpshift'), (9, b'User App Android')]),
        ),
    ]
