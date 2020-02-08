# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0191_auto_20170130_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('what_changed', models.CharField(max_length=32, db_index=True)),
                ('old_value', models.TextField()),
                ('new_value', models.TextField()),
                ('reason_text', models.TextField()),
                ('booking', models.ForeignKey(related_name='booking_change', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='delayreasons',
            options={'verbose_name_plural': 'DelayReasons'},
        ),
        migrations.AddField(
            model_name='delayreasons',
            name='reason_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'Customer ETA changed'), (2, b'Workshop ETA changed')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bookingchange',
            name='delay_reason',
            field=models.ForeignKey(related_name='bc_delay_reason', blank=True, to='core.DelayReasons', null=True),
        ),
        migrations.AddField(
            model_name='bookingchange',
            name='updated_by',
            field=models.ForeignKey(related_name='bc_udpated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
