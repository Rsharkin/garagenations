# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'anuj'

from django.db import migrations
from core.models.booking import BookingInvoice, Booking
from core.models.payment import Payment
from core.managers import bookingManager
from django.db.models import Q

def create_invoices(apps, schema_editor):
    """
    For all bookings, change price of each package and panel.
    """
    #Booking = apps.get_model('core','Booking')

    bookings = Booking.objects.filter(Q(status_id__gte=15,status_id__lte=23)|Q(status_id=25))
    for b in bookings:
        bookingManager.save_invoice(b, update=True)

    payments = Payment.objects.all().select_related('booking').order_by('booking_id','-tx_status')
    for p in payments:
        booking = p.booking
        invoice,bill_dict,msg = bookingManager.save_invoice(booking, update=True)
        p.invoice=invoice
        p.save()
        if p.tx_status == Payment.TX_STATUS_SUCCESS:
            invoice.status = BookingInvoice.INVOICE_STATUS_PAID
            invoice.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0108_auto_20160802_1945'),
    ]

    operations = [
        migrations.RunPython(create_invoices, reverse_code=migrations.RunPython.noop),
    ]
