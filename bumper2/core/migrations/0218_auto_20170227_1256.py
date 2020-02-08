# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0217_auto_20170227_1006'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalScratchFinderLead',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('name', models.CharField(max_length=128)),
                ('phone', models.CharField(max_length=15)),
                ('detail', models.CharField(max_length=2048)),
                ('status', models.PositiveIntegerField(default=1, choices=[(1, b'Open'), (2, b'Verified'), (3, b'Inquiry Created'), (4, b'Fake'), (5, b'RNR'), (6, b'User Already Exist')])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('car_model', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.CarModel', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical scratch finder lead',
            },
        ),
        migrations.CreateModel(
            name='HistoricalUserVendorCash',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('is_promised', models.BooleanField(default=True, db_index=True)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('settled', models.BooleanField(default=False)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('booking', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.Booking', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical user vendor cash',
            },
        ),
        migrations.CreateModel(
            name='IncentiveEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_promised', models.BooleanField(default=True)),
                ('name', models.CharField(help_text=b'This is used in code. Do not change it.', max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('tp_cash', models.DecimalField(help_text=b'Third Party Cash Amount', max_digits=10, decimal_places=2)),
                ('tp', models.PositiveSmallIntegerField(default=1, help_text=b'Third Party Name', choices=[(1, b'PayTM')])),
                ('credit', models.DecimalField(max_digits=10, decimal_places=2)),
                ('expiry_date', models.DateField(help_text=b'Keep it empty if you want this to run unlimited.', null=True, blank=True)),
                ('coupon', models.ForeignKey(blank=True, to='core.Coupon', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ScratchFinderLead',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('phone', models.CharField(max_length=15)),
                ('detail', models.CharField(max_length=2048)),
                ('status', models.PositiveIntegerField(default=1, choices=[(1, b'Open'), (2, b'Verified'), (3, b'Inquiry Created'), (4, b'Fake'), (5, b'RNR'), (6, b'User Already Exist')])),
                ('car_model', models.ForeignKey(blank=True, to='core.CarModel', null=True)),
                ('updated_by', models.ForeignKey(related_name='sflead_updated_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserVendorCash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_promised', models.BooleanField(default=True, db_index=True)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('settled', models.BooleanField(default=False)),
                ('booking', models.ForeignKey(related_name='booking_vendor_cash', blank=True, to='core.Booking', null=True)),
                ('event', models.ForeignKey(to='core.IncentiveEvent')),
                ('user', models.ForeignKey(related_name='user_cash', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='event',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.IncentiveEvent', null=True),
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicaluservendorcash',
            name='user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
