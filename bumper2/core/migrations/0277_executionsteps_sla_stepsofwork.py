# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0276_auto_20170807_2255'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExecutionSteps',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('days_in_workshop', models.IntegerField(help_text=b'Num of days in workshop, excluding sunday')),
                ('portion', models.DecimalField(null=True, max_digits=4, decimal_places=2, blank=True)),
                ('ops_status', models.ForeignKey(related_name='opsstatustodo', to='core.BookingOpsStatus')),
                ('ops_status_to_consider', models.ForeignKey(related_name='opsstatustoconsider', blank=True, to='core.BookingOpsStatus', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sla',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=12)),
                ('filter_conditions', models.CharField(help_text=b'Static Django Query Conditions for filtering the bookings', max_length=1024)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StepsOfWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type_of_damage', models.CharField(max_length=3, choices=[(b'D1', b'D1'), (b'D2', b'D2'), (b'D3', b'D3'), (b'S', b'S'), (b'R1', b'R1'), (b'R2', b'R2'), (b'R3', b'R3')])),
                ('resources_used', models.CharField(help_text=b'user | For optional resource and & for required Together resource', max_length=64)),
                ('processing_time_car_level', models.IntegerField(default=0)),
                ('processing_time_panel_level', models.IntegerField(default=0)),
                ('ops_status', models.ForeignKey(to='core.BookingOpsStatus')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
