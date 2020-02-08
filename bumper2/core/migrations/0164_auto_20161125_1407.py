# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0163_followup_comm_mode'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookingProformaInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, b'Pending'), (2, b'Cancelled'), (3, b'Paid')])),
                ('payable_amt', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('booking', models.ForeignKey(related_name='booking_proforma_invoice', to='core.Booking')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='historicalpayment',
            name='proforma_invoice',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='core.BookingProformaInvoice', null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='proforma_invoice',
            field=models.ForeignKey(related_name='proforma_invoice_payment', blank=True, to='core.BookingProformaInvoice', null=True),
        ),
    ]
