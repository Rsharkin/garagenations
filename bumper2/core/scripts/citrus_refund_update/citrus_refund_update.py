__author__ = 'anuj'

import sys, os, django
sys.path.append('/srv/www/bumper2/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bumper2.settings'
django.setup()
from core.models.booking import Booking, BookingInvoice
from core.models.payment import Payment
from django.utils import timezone
import logging
import decimal

logger = logging.getLogger('bumper.scripts')

# assume that this is only for "replace" type of work.
# get file data
# for each record, if panel id exist - update the prices else create new records with prices.

cur_time = timezone.now()
logger.info("Starting other types for all panels to null script at {}".format(cur_time))

f = open('citrus_refund_update_7_11_2016.csv')
f.next() # this is to avoid processing header

for row in f:
    try:
        row_data = row.strip('\n').strip('\r').split(',')
        logger.info("Processing: {}".format(row_data))
        if row_data[5] == '0':
            continue
        elif row_data[5] == '2':
            b = Booking.objects.filter(id=row_data[0]).first()
            if b:
                bi = BookingInvoice.objects.filter(status__in=[1,3]).order_by('-id').first()
                if bi:
                    payment_amt = decimal.Decimal(row_data[2])
                    refund = Payment.objects.create(
                       invoice=bi,
                       tx_status=Payment.TX_STATUS_SUCCESS,
                       tx_type=Payment.TX_TYPE_REFUND,
                       vendor_status="Success",
                       mode=Payment.PAYMENT_MODE_ONLINE,
                       vendor=Payment.VENDOR_CITRUS_PAY,
                       amount=payment_amt,
                       payment_vendor_id='',
                       error_message="Success",
                       tx_data="Created by System Script.",
                    )
                    logger.error("Refund entry created: {}".format(refund.id))
                else:
                    logger.error("Booking Invoice not there.")
        elif row_data[5] == '3':
            b = Booking.objects.filter(id=row_data[0]).first()
            if b:
                bi = BookingInvoice.objects.filter(status__in=[1, 3]).order_by('-id').first()
                if bi:
                    payment_amt = decimal.Decimal(row_data[2])
                    trx = Payment.objects.create(
                        invoice=bi,
                        tx_status=Payment.TX_STATUS_SUCCESS,
                        tx_type=Payment.TX_TYPE_PAYMENT,
                        vendor_status="Success",
                        mode=Payment.PAYMENT_MODE_ONLINE,
                        vendor=Payment.VENDOR_CITRUS_PAY,
                        amount=payment_amt,
                        payment_vendor_id='',
                        error_message="Success",
                        tx_data="Created by System Script.",
                    )
                    refund = Payment.objects.create(
                        invoice=bi,
                        tx_status=Payment.TX_STATUS_SUCCESS,
                        tx_type=Payment.TX_TYPE_REFUND,
                        vendor_status="Success",
                        mode=Payment.PAYMENT_MODE_ONLINE,
                        vendor=Payment.VENDOR_CITRUS_PAY,
                        amount=payment_amt,
                        payment_vendor_id='',
                        error_message="Success",
                        tx_data="Created by System Script.",
                    )
                    logger.error("Trx and refund entry created: {}, {}".format(trx.id,refund.id))
                else:
                    logger.error("Booking Invoice not there.")
    except:
        logger.exception("Error in line: {}".format(row))

cur_time = timezone.now()
logger.info("Ending update panel price to null script at {}".format(cur_time))
