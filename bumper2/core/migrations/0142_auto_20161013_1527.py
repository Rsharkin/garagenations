# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0141_auto_20161010_1254'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingOpsAlerts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('time_to_send', models.DateTimeField()),
                ('alert_status', models.PositiveSmallIntegerField(choices=[(1, b'Pending'), (2, b'Sent'), (3, b'Cancelled')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OpsAlertType',
            fields=[
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('time_diff', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='packageprice',
            name='dealer_price',
        ),
        migrations.AddField(
            model_name='packageprice',
            name='dealer_labour_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='packageprice',
            name='dealer_material_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='packageprice',
            name='dealer_part_price',
            field=models.DecimalField(default=0, help_text=b'Inclusive of Tax', max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='packageprice',
            name='show_savings',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bookingopsalerts',
            name='alert_type',
            field=models.ForeignKey(to='core.OpsAlertType'),
        ),
        migrations.AddField(
            model_name='bookingopsalerts',
            name='booking',
            field=models.ForeignKey(related_name='booking_opsalert', to='core.Booking'),
        ),
    ]
