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
    help = 'Script:: DAILY_PAYMENTS:: Process daily payments - get latest status from Citrus Pay.'

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: DAILY_PAYMENTS:: Script started - current_time: %s" % current_time)

        #f = open('/var/log/bumper2/payment/daily_payment_%s.csv' % str(current_time.date()),'w')
        try:
            txnStartDate = (current_time - timezone.timedelta(days=1)).date()
            txnEndDate = current_time.date()
            headers = {"access_key":settings.CITRUS_MERCHANT_ACCESS_KEY, "Accept":"application/json", "Content-Type":"application/json"}

            data = {"txnStartDate":str(txnStartDate),"txnEndDate":str(txnEndDate),"fromPosition":0}

            url = "https://admin.citruspay.com/api/v2/txn/search"

            r = requests.post(url, headers=headers, json=data)

            output = r.json()
            trxs = output.get("transactions")

            # w = csv.writer(f)
            # header = ["Booking Id","Status","Difference"]
            # w.writerow(header)

            SUCCESS_TRX = "Transaction successful"
            REFUND_TRX = "Refund successful"
            PENDING_TRX = "Transaction forwarded to PG"
            for trx in trxs:
                merchant_id = trx['merchantTxnId']
                p = Payment.objects.filter(merchant_trx_id=merchant_id, tx_status = Payment.TX_STATUS_PENDING).first()
                if p:
                    amount_received = trx['amount']
                    amount_received = decimal.Decimal(amount_received[:-4])
                    if trx['respMsg'] == SUCCESS_TRX:
                        p.tx_status = Payment.TX_STATUS_SUCCESS
                        p.amount = amount_received
                        p.payment_vendor_id = trx.get('txnId')
                        p.vendor_status = trx['respMsg']
                        p.save()
                        logger.info("Script:: DAILY_PAYMENTS:: Success Payment processed for merchant trx id: {}".format(merchant_id))
                    elif trx['respMsg'] == REFUND_TRX:
                        pass
                    elif trx['respMsg'] == PENDING_TRX:
                        pass
                    # else:
                    #     p.tx_status = Payment.TX_STATUS_FAILED
                    #     p.amount = amount_received
                    #     p.payment_vendor_id = trx.get('txnId')
                    #     p.vendor_status = trx['respMsg']
                    #     p.save()
                    #     logger.info("Script:: DAILY_PAYMENTS:: Failed Payment processed for merchant trx id: {}".format(merchant_id))
                else:
                    logger.info("Script:: DAILY_PAYMENTS:: Payment not found for merchant trx id: {}".format(merchant_id))
        except:
            logger.exception("Script:: DAILY_PAYMENTS:: Failed to get data from citrus pay.")
        #f.close()
