# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0279_auto_20170808_1313'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingExpectedEOD',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('for_date', models.DateField()),
                ('booking', models.ForeignKey(related_name='booking_expected_eods', to='core.Booking')),
                ('ops_status', models.ForeignKey(related_name='expected_epd_ops_status', to='core.BookingOpsStatus')),
                ('status', models.ForeignKey(related_name='expected_eod_status', to='core.BookingStatus')),
                ('updated_by', models.ForeignKey(related_name='expected_eod_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
