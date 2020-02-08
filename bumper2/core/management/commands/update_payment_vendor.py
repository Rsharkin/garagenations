"""
Process pending Payments - Or Update Payment statuses
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models.payment import Payment
from core.models.booking import Booking, BookingInvoice
import requests
import decimal
from django.conf import settings
import csv
import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = 'Script:: UPDATE_VENDOR:: Update Vendor - get latest status from Citrus Pay.'

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: UPDATE_VENDOR:: Script started - current_time: %s" % current_time)

        f = open('citrus_trx.csv','w')
        try:
            headers = {"access_key":settings.CITRUS_MERCHANT_ACCESS_KEY, "Accept":"application/json", "Content-Type":"application/json"}

            data = {"txnStartDate":"20160701","txnEndDate":"20160831","fromPosition":0}

            url = "https://admin.citruspay.com/api/v2/txn/search"

            r = requests.post(url, headers=headers, json=data)

            output = r.json()
            trxs = output.get("transactions")

            w = csv.writer(f)
            header = ["Booking Id","Status","Difference"]
            w.writerow(header)

            SUCCESS_TRX = "Transaction successful"
            REFUND_TRX = "Refund successful"
            booking_dict = {}
            vendor_id_dict = {}
            for trx in trxs:
                merchant_id = trx['merchantTxnId']
                if trx['respMsg'] in (SUCCESS_TRX,REFUND_TRX):
                    booking_id = merchant_id.split('BUMP')[0]
                    amount_received = trx['amount']
                    amount_received = decimal.Decimal(amount_received[:-4])
                    if trx['respMsg'] == SUCCESS_TRX:
                        booking_dict[booking_id] = booking_dict.setdefault(booking_id,decimal.Decimal('0.00')) + amount_received
                        vendor_id_dict.setdefault(booking_id, []).append(trx['txnId'])
                    elif trx['respMsg'] == REFUND_TRX:
                        booking_dict[booking_id] = booking_dict.setdefault(booking_id,decimal.Decimal('0.00')) - amount_received
                        vendor_id_dict.setdefault(booking_id, []).append(trx['txnId'])

            for booking_id, amount_received in booking_dict.iteritems():
                b = Booking.objects.filter(id=booking_id)
                if b:
                    booking_invoices = BookingInvoice.objects.filter(booking=b)
                    payments = Payment.objects.filter(invoice__in=booking_invoices, tx_status=Payment.TX_STATUS_SUCCESS)

                    sum_received = decimal.Decimal('0.00')
                    if payments:
                        for p in payments:
                            if p.tx_type == Payment.TX_TYPE_REFUND:
                                sum_received -= p.amount
                            else:
                                sum_received += p.amount

                    if sum_received != amount_received:
                        logger.info("Script:: DAILY_PAYMENTS:: booking_id: %s, amount from citrus: %s, amount in system: %s", booking_id,
                                    amount_received, sum_received)
                        invoice = BookingInvoice.objects.filter(booking=b).exclude(status=BookingInvoice.INVOICE_STATUS_CANCELLED).order_by('-created_at').first()
                        vendor_status = None
                        payment_amt = decimal.Decimal('0.00')
                        vendor_id = ','.join(vendor_id_dict[booking_id])
                        tx_type = Payment.TX_TYPE_PAYMENT
                        if sum_received > amount_received:
                            vendor_status = REFUND_TRX
                            payment_amt = sum_received - amount_received
                            tx_type = Payment.TX_TYPE_REFUND
                            w.writerow([booking_id,"Refund",sum_received-amount_received])
                        else:
                            vendor_status = SUCCESS_TRX
                            payment_amt = amount_received - sum_received
                            w.writerow([booking_id,"Transaction",amount_received-sum_received])
                        #new_payment = Payment.objects.create(
                        #    invoice=invoice,
                        #    tx_status=Payment.TX_STATUS_SUCCESS,
                        #    tx_type=tx_type,
                        #    vendor_status=vendor_status,
                        #    mode=Payment.PAYMENT_MODE_ONLINE,
                        #    vendor=Payment.VENDOR_CITRUS_PAY,
                        #    amount=payment_amt,
                        #    payment_vendor_id=vendor_id,
                        #    error_message="Success",
                        #    tx_data="Created by System Script.",
                        #)
                        logger.info("Script:: DAILY_PAYMENTS:: Payment created for vendor status: %s",vendor_status)
                    if len(payments) == 1:
                        payments.update(vendor=Payment.VENDOR_CITRUS_PAY)
                else:
                    logger.info("Script:: DAILY_PAYMENTS:: Booking Id %s not found", booking_id)
                    w.writerow([booking_id,"Booking Id not found",0])
        except:
            logger.exception("Script:: DAILY_PAYMENTS:: Failed to get data from citrus pay.")
        f.close()
