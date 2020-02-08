# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0257_auto_20170706_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarColor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('color_name', models.CharField(unique=True, max_length=20)),
                ('color_code', models.CharField(max_length=20, null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='credittransaction',
            name='entity',
            field=models.CharField(blank=True, max_length=64, null=True, choices=[(b'Booking', b'Booking'), (b'Referral', b'Referral'), (b'BumperUser', b'BumperUser')]),
        ),
        migrations.AlterField(
            model_name='followup',
            name='comm_mode',
            field=models.PositiveSmallIntegerField(default=1, help_text=b'How was the customer communicated?', choices=[(1, b'Call'), (2, b'WhatsApp'), (3, b'SMS'), (4, b'Email'), (5, b'Executive App'), (6, b'Push'), (7, b'Web Chat'), (8, b'Helpshift'), (9, b'User App')]),
        ),
        migrations.AlterField(
            model_name='historicaluservendorcash',
            name='entity',
            field=models.CharField(blank=True, max_length=64, null=True, choices=[(b'Booking', b'Booking'), (b'ScratchFinderLead', b'ScratchFinderLead'), (b'BumperUser', b'BumperUser')]),
        ),
        migrations.AlterField(
            model_name='uservendorcash',
            name='entity',
            field=models.CharField(blank=True, max_length=64, null=True, choices=[(b'Booking', b'Booking'), (b'ScratchFinderLead', b'ScratchFinderLead'), (b'BumperUser', b'BumperUser')]),
        ),
        migrations.AddField(
            model_name='carmodel',
            name='colors',
            field=models.ManyToManyField(to='core.CarColor'),
        ),
    ]
