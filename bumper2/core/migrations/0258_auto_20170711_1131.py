# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0257_auto_20170706_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkshopResources',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('for_date', models.DateField()),
                ('denters', models.IntegerField()),
                ('painters', models.IntegerField()),
                ('painter_helpers', models.IntegerField()),
                ('paint_booth', models.IntegerField(default=1, null=True, blank=True)),
                ('washing_bay', models.IntegerField(default=1, null=True, blank=True)),
                ('type_of_record', models.IntegerField(default=1)),
                ('workshop', models.ForeignKey(related_name='workshopresource', to='core.Workshop')),
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
    ]
