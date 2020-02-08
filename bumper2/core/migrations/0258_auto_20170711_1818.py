# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0257_auto_20170706_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingPartDoc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('quote_eta', models.DateTimeField(null=True, blank=True)),
                ('quote_eta_reason', models.TextField(null=True, blank=True)),
                ('booking_part', models.ForeignKey(related_name='booking_part', to='core.BookingPackagePanel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BookingPartQuote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('part_number', models.CharField(max_length=64)),
                ('price', models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2)),
                ('eta', models.DateTimeField()),
                ('quote_type', models.PositiveSmallIntegerField(choices=[(1, b'OEM'), (2, b'After Market'), (3, b'Refurbished')])),
                ('booking_part_doc', models.ForeignKey(related_name='booking_part_doc', to='core.BookingPartDoc')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalBookingPartDoc',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('quote_eta', models.DateTimeField(null=True, blank=True)),
                ('quote_eta_reason', models.TextField(null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('booking_part', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingPackagePanel', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical booking part doc',
            },
        ),
        migrations.CreateModel(
            name='HistoricalBookingPartQuote',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('part_number', models.CharField(max_length=64)),
                ('price', models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2)),
                ('eta', models.DateTimeField()),
                ('quote_type', models.PositiveSmallIntegerField(choices=[(1, b'OEM'), (2, b'After Market'), (3, b'Refurbished')])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('booking_part_doc', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingPartDoc', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical booking part quote',
            },
        ),
        migrations.CreateModel(
            name='PartDocNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField()),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PartDocStatus',
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
            name='PartQuoteNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField()),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PartVendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=128)),
                ('active', models.BooleanField(default=True)),
                ('address', models.TextField()),
                ('city', models.ForeignKey(to='core.City')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='usercar',
            name='manufactured_on',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='usercar',
            name='variant',
            field=models.ForeignKey(blank=True, to='core.CarModelVariant', null=True),
        ),
        migrations.AddField(
            model_name='usercar',
            name='vin_no',
            field=models.CharField(max_length=32, null=True, blank=True),
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
            model_name='historicalbookingpartquote',
            name='vendor',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.PartVendor', null=True),
        ),
        migrations.AddField(
            model_name='historicalbookingpartdoc',
            name='status',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.PartDocStatus', null=True),
        ),
        migrations.AddField(
            model_name='bookingpartquote',
            name='notes',
            field=models.ManyToManyField(to='core.PartDocNote'),
        ),
        migrations.AddField(
            model_name='bookingpartquote',
            name='vendor',
            field=models.ForeignKey(to='core.PartVendor'),
        ),
        migrations.AddField(
            model_name='bookingpartdoc',
            name='notes',
            field=models.ManyToManyField(to='core.PartDocNote'),
        ),
        migrations.AddField(
            model_name='bookingpartdoc',
            name='status',
            field=models.ForeignKey(to='core.PartDocStatus'),
        ),
    ]
