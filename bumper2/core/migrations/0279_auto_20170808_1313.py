# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0278_executionsteps_sla'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkshopExecutionSteps',
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
            name='WorkshopStepsOfWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type_of_damage', models.CharField(max_length=3, choices=[(b'D1', b'D1'), (b'D2', b'D2'), (b'D3', b'D3'), (b'S', b'S'), (b'R1', b'R1'), (b'R2', b'R2'), (b'R3', b'R3')])),
                ('resources_used', models.CharField(help_text=b'user | For optional resource and & for required Together resource', max_length=64)),
                ('processing_time_car_level', models.IntegerField(default=0, help_text=b'In minutes')),
                ('processing_time_panel_level', models.IntegerField(default=0, help_text=b'In minutes')),
                ('ops_status', models.ForeignKey(to='core.BookingOpsStatus')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameModel(
            old_name='Sla',
            new_name='WorkshopSla',
        ),
        migrations.RemoveField(
            model_name='executionsteps',
            name='ops_status',
        ),
        migrations.RemoveField(
            model_name='executionsteps',
            name='ops_status_to_consider',
        ),
        migrations.RemoveField(
            model_name='executionsteps',
            name='sla',
        ),
        migrations.RemoveField(
            model_name='stepsofwork',
            name='ops_status',
        ),
        migrations.DeleteModel(
            name='ExecutionSteps',
        ),
        migrations.DeleteModel(
            name='StepsOfWork',
        ),
        migrations.AddField(
            model_name='workshopexecutionsteps',
            name='sla',
            field=models.ForeignKey(to='core.WorkshopSla'),
        ),
    ]
