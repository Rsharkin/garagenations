# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0088_auto_20160704_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalBookingPackagePanel',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('price', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('service_tax', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('vat', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('booking_package', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingPackage', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical booking package panel',
            },
        ),
        migrations.CreateModel(
            name='PartnerLead',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=256, null=True, blank=True)),
                ('mobile', models.CharField(db_index=True, max_length=15, null=True, blank=True)),
                ('email', models.EmailField(max_length=256, null=True, blank=True)),
                ('city', models.CharField(max_length=256, null=True, blank=True)),
                ('workshop_name', models.CharField(max_length=256, null=True, blank=True)),
                ('car', models.CharField(max_length=512, null=True, blank=True)),
                ('message', models.CharField(max_length=512, null=True, blank=True)),
                ('utm_source', models.CharField(max_length=512, null=True, blank=True)),
                ('utm_mode', models.CharField(max_length=512, null=True, blank=True)),
                ('utm_campaign', models.CharField(max_length=512, null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='bumperuser',
            name='source',
            field=models.CharField(blank=True, max_length=5, null=True, choices=[(b'web', b'Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber')]),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='historicalbookingpackagepanel',
            name='panel',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.CarPanelPrice', null=True),
        ),
    ]
