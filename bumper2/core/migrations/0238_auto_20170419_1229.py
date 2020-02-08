# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0237_auto_20170411_1310'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FlagType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalDriverLocation',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('latitude', models.DecimalField(max_digits=11, decimal_places=8)),
                ('longitude', models.DecimalField(max_digits=11, decimal_places=8)),
                ('direction', models.PositiveSmallIntegerField(choices=[(1, b'DriverToCustPick'), (2, b'CustToDriverPick'), (3, b'DriverToCustDrop'), (4, b'DriverCurrentLoc')])),
                ('track_time', models.DateTimeField()),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('driver', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical driver location',
            },
        ),
        migrations.AlterField(
            model_name='booking',
            name='rework_booking',
            field=models.ForeignKey(related_name='booking_rework', blank=True, to='core.Booking', help_text=b"if booking A is there and Booking B is reowork of it, then A's Id will be there in B.", null=True),
        ),
        migrations.AlterField(
            model_name='scratchfinderlead',
            name='user',
            field=models.ForeignKey(help_text=b'User that submitted this lead.', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bookingflag',
            name='booking',
            field=models.ForeignKey(related_name='booking_flag', to='core.Booking'),
        ),
        migrations.AddField(
            model_name='bookingflag',
            name='flag_type',
            field=models.ForeignKey(to='core.FlagType'),
        ),
    ]
