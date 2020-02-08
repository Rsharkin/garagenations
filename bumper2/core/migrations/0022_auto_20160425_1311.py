# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20160425_1224'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalBooking',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('updated_at', models.DateTimeField(editable=False, blank=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('source', models.CharField(blank=True, max_length=5, null=True, choices=[(b'web', b'Web'), (b'email', b'Email'), (b'sms', b'SMS'), (b'chat', b'Chat'), (b'call', b'Call'), (b'app', b'App'), (b'event', b'Event'), (b'uber', b'Uber')])),
                ('desc', models.CharField(max_length=2048, null=True)),
                ('pickup_time', models.DateTimeField(null=True)),
                ('drop_time', models.DateTimeField(null=True)),
                ('estimate_pickup_time', models.DateTimeField(null=True)),
                ('actual_pickup_time', models.DateTimeField(null=True)),
                ('actual_drop_time', models.DateTimeField(null=True)),
                ('actual_pickup_address', models.CharField(max_length=256, null=True)),
                ('estimate_complete_time', models.DateTimeField(null=True)),
                ('estimate_drop_time', models.DateTimeField(null=True)),
                ('actual_drop_address', models.CharField(max_length=256, null=True)),
                ('next_followup', models.DateTimeField(help_text=b'Next Followup date.', null=True, blank=True)),
                ('reason_for_cancellation_desc', models.CharField(max_length=512, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('assigned_to', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('cancel_reason_dd', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.CancellationReasons', null=True)),
                ('city', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.City', null=True)),
                ('drop_address', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.UserAddress', null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('pickup_address', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.UserAddress', null=True)),
                ('status', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingStatus', null=True)),
                ('sub_status', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingSubStatus', null=True)),
                ('user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('usercar', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.UserCar', null=True)),
                ('workshop', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.Workshop', null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical booking',
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='actual_drop_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='actual_pickup_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='assigned_to',
            field=models.ForeignKey(related_name='booking_assigned_to', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='cancel_reason_dd',
            field=models.ForeignKey(to='core.CancellationReasons', null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='desc',
            field=models.CharField(max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='drop_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='estimate_complete_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='estimate_drop_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='estimate_pickup_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='next_followup',
            field=models.DateTimeField(help_text=b'Next Followup date.', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='pickup_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='reason_for_cancellation_desc',
            field=models.CharField(max_length=512, null=True),
        ),
    ]
