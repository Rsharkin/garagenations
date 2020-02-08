# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0128_auto_20160827_1813'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalUserInquiry',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('inquiry', models.CharField(max_length=2048)),
                ('status', models.PositiveIntegerField(default=1, choices=[(1, b'Open'), (2, b'Postponed'), (3, b'Following Up'), (4, b'Closed - Booking created'), (5, b'RNR'), (6, b'Closed - Booking not created'), (7, b'Delayed Ops'), (9, b'Closed - Booking created before followup'), (8, b'Duplicate'), (10, b'Closed - Price Issue'), (11, b'Closed - Trust Issue')])),
                ('source', models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'helpshift', b'Helpshift')])),
                ('reference', models.CharField(max_length=1048, null=True, blank=True)),
                ('lead_quality', models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'High'), (2, b'Medium'), (3, b'Low')])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical user inquiry',
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'High'), (2, b'Medium'), (3, b'Low')]),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'High'), (2, b'Medium'), (3, b'Low')]),
        ),
        migrations.AddField(
            model_name='userinquiry',
            name='lead_quality',
            field=models.PositiveSmallIntegerField(blank=True, null=True, choices=[(1, b'High'), (2, b'Medium'), (3, b'Low')]),
        ),
        migrations.AlterField(
            model_name='booking',
            name='followup',
            field=models.ManyToManyField(related_name='booking_followup', to='core.Followup', blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral')]),
        ),
        migrations.AlterField(
            model_name='bumperuser',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'helpshift', b'Helpshift')]),
        ),
        migrations.AlterField(
            model_name='historicalbooking',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral')]),
        ),
        migrations.AlterField(
            model_name='userinquiry',
            name='source',
            field=models.CharField(blank=True, max_length=12, null=True, choices=[(b'web', b'Web'), (b'mobile-web', b'Mobile Web'), (b'desktop-web', b'Desktop Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber'), (b'opsPanel', b'opsPanel'), (b'android', b'android'), (b'iphone', b'iphone'), (b'facebook', b'Facebook'), (b'referral', b'Referral'), (b'helpshift', b'Helpshift')]),
        ),
        migrations.AlterField(
            model_name='userinquiry',
            name='status',
            field=models.PositiveIntegerField(default=1, choices=[(1, b'Open'), (2, b'Postponed'), (3, b'Following Up'), (4, b'Closed - Booking created'), (5, b'RNR'), (6, b'Closed - Booking not created'), (7, b'Delayed Ops'), (9, b'Closed - Booking created before followup'), (8, b'Duplicate'), (10, b'Closed - Price Issue'), (11, b'Closed - Trust Issue')]),
        ),
        migrations.AddField(
            model_name='historicaluserinquiry',
            name='assigned_to',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicaluserinquiry',
            name='car_model',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.CarModel', null=True),
        ),
        migrations.AddField(
            model_name='historicaluserinquiry',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicaluserinquiry',
            name='user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
