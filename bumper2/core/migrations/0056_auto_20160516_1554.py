# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_usercredit'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingDiscount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('discount', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('booking', models.ForeignKey(related_name='booking_discount', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='billitem',
            name='bill',
        ),
        migrations.RemoveField(
            model_name='billitem',
            name='package',
        ),
        migrations.RemoveField(
            model_name='bookingbill',
            name='booking',
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='service_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackage',
            name='vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='service_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookingpackagepanel',
            name='vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='service_tax',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='historicalbookingpackage',
            name='vat',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.DeleteModel(
            name='BillItem',
        ),
        migrations.DeleteModel(
            name='BookingBill',
        ),
    ]
