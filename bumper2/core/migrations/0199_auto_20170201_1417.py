# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0198_auto_20170201_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingHandoverItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.PositiveIntegerField()),
                ('has_issue', models.BooleanField(default=False)),
                ('issue_reason', models.CharField(max_length=1024, null=True, blank=True)),
                ('booking', models.ForeignKey(related_name='booking_handover_item', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HandoverItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=512)),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='bookinghandoveritem',
            name='item',
            field=models.ForeignKey(to='core.HandoverItem'),
        ),
        migrations.AddField(
            model_name='bookinghandoveritem',
            name='updated_by',
            field=models.ForeignKey(related_name='bhi_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
