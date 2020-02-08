# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0230_auto_20170322_1200'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryReasons',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(max_length=64)),
                ('active', models.BooleanField(default=True)),
                ('order_num', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='delivery_reason_desc',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='delivery_reason_desc',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='delivery_reason',
            field=models.ForeignKey(related_name='booking_delivery_reason', blank=True, to='core.DeliveryReasons', null=True),
        ),
        migrations.AddField(
            model_name='historicalbooking',
            name='delivery_reason',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.DeliveryReasons', null=True),
        ),
    ]
