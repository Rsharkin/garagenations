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
    help = 'Script:: DAILY_PAYMENTS:: Process daily payments - get latest status from Razor Pay.'

    def add_arguments(self, parser):
        parser.add_argument('txnStartDate', type=str)
        parser.add_argument('txnEndDate', type=str)

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: DAILY_PAYMENTS:: Script started - current_time: %s" % current_time)

        f = open('razorpay_trx.csv','w')
        try:
            url = 'https://api.razorpay.com/v1/payments'
            skip = 0
            import datetime, dateutil.parser, time

            from_date = dateutil.parser.parse(options['txnStartDate']+'T00:00:00')
            to_date = dateutil.parser.parse(options['txnEndDate']+'T00:00:00')

            data = {"from": int(time.mktime(from_date.timetuple())),
                    "to": int(time.mktime(to_date.timetuple())), "count": 100, "skip": skip}
            output = []
            while True:
                resp = requests.get(url, params=data, auth=(settings.RAZOR_PAY_API_KEY, settings.RAZOR_PAY_API_SECRET))
                output_json = resp.json()
                if not output_json or not output_json.get("count", None):
                    break
                output.extend(resp.json().get("items", []))
                skip += 100
                data["skip"] = skip

            logger.info("Script:: DAILY_PAYMENTS:: data from razorpay --- {} ".format(output))

            w = csv.writer(f)
            header = ["Booking Id","Status","Amount in System","Vendor Amount","Difference"]
            w.writerow(header)

            SUCCESS_TRX = "captured"
            REFUND_TRX = "refunded"
            booking_dict = {}
            vendor_id_dict = {}
            for trx in output:
                if trx.get('status') in (SUCCESS_TRX,REFUND_TRX):
                    booking_id = trx.get("notes", {}).get("bookingId")
                    amount_received = trx.get('amount')
                    amount_refunded = decimal.Decimal(trx.get('amount_refunded', '0.00'))/100
                    amount_received = decimal.Decimal(amount_received/100)
                    booking_dict[booking_id] = booking_dict.setdefault(booking_id,
                                                                       decimal.Decimal('0.00')) + amount_received - amount_refunded
                    vendor_id_dict.setdefault(booking_id, []).append(trx.get('id'))
                # else:
                #     logger.info("Script:: DAILY_PAYMENTS:: invalid merchant txn id --- {}, respMsg -- {} ".format(
                #                                                                                     merchant_id,
                #                                                                                     trx['respMsg']))

            for booking_id, amount_received in booking_dict.iteritems():
                b = Booking.objects.filter(id=booking_id).first()
                if not b:
                    booking_invoices = BookingInvoice.objects.filter(id=booking_id).first()
                    if not booking_invoices:
                        logger.info("Script:: DAILY_PAYMENTS:: Booking Id %s not found", booking_id)
                        w.writerow([booking_id,"Booking Id not found","NA","NA",0])
                        continue
                else:
                    booking_invoices = BookingInvoice.objects.filter(booking=b)
                payments = Payment.objects.filter(invoice__in=booking_invoices, tx_status=Payment.TX_STATUS_SUCCESS,
                                                  vendor=Payment.VENDOR_RAZOR_PAY)

                sum_received = decimal.Decimal('0.00')
                if payments:
                    for p in payments:
                        if p.tx_type == Payment.TX_TYPE_REFUND:
                            sum_received -= p.amount
                        else:
                            sum_received += p.amount

                sum_received = decimal.Decimal(sum_received)
                amount_received = decimal.Decimal(amount_received)

                if sum_received != amount_received:
                    logger.info("Script:: DAILY_PAYMENTS:: booking_id: %s, amount from razorpay: %s, amount in system: %s", booking_id,
                                amount_received, sum_received)
                    # invoice = BookingInvoice.objects.filter(booking=b).exclude(status=BookingInvoice.INVOICE_STATUS_CANCELLED).order_by('-created_at').first()
                    vendor_status = None
                    payment_amt = decimal.Decimal('0.00')
                    vendor_id = ','.join(vendor_id_dict[booking_id])
                    tx_type = Payment.TX_TYPE_PAYMENT
                    if decimal.Decimal(sum_received) > decimal.Decimal(amount_received):
                        vendor_status = REFUND_TRX
                        payment_amt = sum_received - amount_received
                        tx_type = Payment.TX_TYPE_REFUND
                        w.writerow([booking_id,"Refund",sum_received,amount_received,sum_received-amount_received])

                    else:
                        vendor_status = SUCCESS_TRX
                        payment_amt = amount_received - sum_received
                        w.writerow(
                            [booking_id, "Transaction", sum_received, amount_received, amount_received - sum_received])

                    # new_payment = Payment.objects.create(
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
                    # )
                    logger.info("Script:: DAILY_PAYMENTS:: Payment created for vendor status: %s", vendor_status)
        except:
            logger.exception("Script:: DAILY_PAYMENTS:: Failed to get data from razor pay.")
        f.close()
