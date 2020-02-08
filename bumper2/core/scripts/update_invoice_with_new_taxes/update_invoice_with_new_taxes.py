__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from core.models.booking import BookingInvoice
from core.managers.bookingManager import save_invoice
from django.utils import timezone
import logging

logger = logging.getLogger('bumper.scripts')

cur_time = timezone.now()
logger.info("Starting update invoice with new taxes script at {}".format(cur_time))

booking_invoices = BookingInvoice.objects.exclude(status=BookingInvoice.INVOICE_STATUS_CANCELLED).select_related('booking')
for bi in booking_invoices:
    save_invoice(bi.booking, update=True, ignore_new=True)

cur_time = timezone.now()
logger.info("Ending update invoice with new taxes script at {}".format(cur_time))
