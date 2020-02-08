# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0102_auto_20160731_2113'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, b'Pending'), (2, b'Cancelled'), (3, b'Paid')])),
                ('payable_amt', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('amt_wo_discount', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('labour_price', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('part_price', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('material_price', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('vat', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('service_tax', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('kk_tax', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('sb_tax', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('booking', models.ForeignKey(related_name='booking_invoice', to='core.Booking')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='bookingpackage',
            name='labour_kk_tax',
        ),
        migrations.RemoveField(
            model_name='bookingpackage',
            name='labour_sb_tax',
        ),
        migrations.RemoveField(
            model_name='bookingpackage',
            name='labour_service_tax',
        ),
        migrations.RemoveField(
            model_name='bookingpackage',
            name='material_vat',
        ),
        migrations.RemoveField(
            model_name='bookingpackage',
            name='part_vat',
        ),
        migrations.RemoveField(
            model_name='bookingpackage',
            name='service_tax',
        ),
        migrations.RemoveField(
            model_name='bookingpackage',
            name='vat',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='labour_kk_tax',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='labour_sb_tax',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='labour_service_tax',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='material_vat',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='part_vat',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='service_tax',
        ),
        migrations.RemoveField(
            model_name='bookingpackagepanel',
            name='vat',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackage',
            name='labour_kk_tax',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackage',
            name='labour_sb_tax',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackage',
            name='labour_service_tax',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackage',
            name='material_vat',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackage',
            name='part_vat',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackage',
            name='service_tax',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackage',
            name='vat',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackagepanel',
            name='labour_kk_tax',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackagepanel',
            name='labour_sb_tax',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackagepanel',
            name='labour_service_tax',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackagepanel',
            name='material_vat',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackagepanel',
            name='part_vat',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackagepanel',
            name='service_tax',
        ),
        migrations.RemoveField(
            model_name='historicalbookingpackagepanel',
            name='vat',
        ),
        migrations.AddField(
            model_name='historicalpayment',
            name='invoice',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingInvoice', null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice',
            field=models.ForeignKey(related_name='invoice_payment', blank=True, to='core.BookingInvoice', null=True),
        ),
    ]
