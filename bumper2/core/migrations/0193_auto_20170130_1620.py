# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0192_auto_20170130_1510'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingChangeLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('what_changed', models.CharField(max_length=32, db_index=True)),
                ('old_value', models.TextField()),
                ('new_value', models.TextField()),
                ('reason_text', models.TextField()),
                ('booking', models.ForeignKey(related_name='booking_change', to='core.Booking')),
                ('delay_reason', models.ForeignKey(related_name='bc_delay_reason', blank=True, to='core.DelayReasons', null=True)),
                ('updated_by', models.ForeignKey(related_name='bc_udpated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='bookingchange',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='bookingchange',
            name='delay_reason',
        ),
        migrations.RemoveField(
            model_name='bookingchange',
            name='updated_by',
        ),
        migrations.DeleteModel(
            name='BookingChange',
        ),
    ]
