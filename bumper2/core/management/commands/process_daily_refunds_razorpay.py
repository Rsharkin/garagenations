"""
Process pending Payments - Or Update Payment statuses
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models.payment import Payment
from core.models.booking import Booking, BookingInvoice, BookingProformaInvoice
import requests
import decimal
from django.conf import settings
import csv
import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = 'Script:: DAILY_PAYMENTS:: Process daily refunds - get refunds done today in razorpay'

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: DAILY_REFUNDS_RAZORPAY:: Script started - current_time: %s" % current_time)

        #f = open('/var/log/bumper2/payment/daily_payment_%s.csv' % str(current_time.date()),'w')
        try:
            txnStartDate = (current_time - timezone.timedelta(days=1)).replace(hour=0,minute=0,second=0)
            txnEndDate = current_time.replace(hour=0,minute=0,second=0)

            url = 'https://api.razorpay.com/v1/refunds'
            skip = 0
            import datetime, time

            from_date = txnStartDate
            to_date = txnEndDate

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

            for trx in output:
                rzrpay_payment_id = trx.get("payment_id")
                payment_url = 'https://api.razorpay.com/v1/payments/{}'.format(rzrpay_payment_id)

                resp = requests.get(payment_url, params={},
                                    auth=(settings.RAZOR_PAY_API_KEY, settings.RAZOR_PAY_API_SECRET))
                if not resp.status_code == 200:
                    logger.info("Script:: DAILY_REFUNDS_RAZORPAY:: Razorpay Payment Id :%s not found" % rzrpay_payment_id)
                    continue
                payment_json = resp.json()
                if not payment_json:
                    logger.info("Script:: DAILY_REFUNDS_RAZORPAY:: Razorpay Payment Id :%s not found" % rzrpay_payment_id)
                    continue

                notes = payment_json.get("notes", {})
                if not notes:
                    logger.info("Script:: DAILY_REFUNDS_RAZORPAY:: Razorpay Payment Id :%s No notes found" % rzrpay_payment_id)
                    continue
                booking_id = notes.get("bookingId")
                amount_refunded = decimal.Decimal(trx.get('amount', '0.00')) / 100
                rzrpay_refund_id = trx.get("id")
                logger.info(
                    "Script:: DAILY_REFUNDS_RAZORPAY:: Processing for booking_id: {}, "
                    "rzrpay_payment_id: {}, rzrpay_refund_id: {}".format(booking_id, rzrpay_payment_id, rzrpay_refund_id))

                booking_invoice = BookingInvoice.objects.filter(booking_id=booking_id, status__in=[1,3]).first()
                refund_obj = Payment.objects.filter(payment_vendor_id=rzrpay_refund_id, invoice=booking_invoice).first()
                if refund_obj:
                    logger.info("Script:: DAILY_REFUNDS_RAZORPAY:: Booking Id :%s Refund already exist" % booking_id)
                    continue
                proforma_invoice = None
                if not booking_invoice:
                    proforma_invoice = BookingProformaInvoice.objects.filter(booking_id=booking_id,
                                                                             status__in=[1, 3]).first()
                    refund_obj = Payment.objects.filter(payment_vendor_id=rzrpay_refund_id,
                                                        proforma_invoice=proforma_invoice).first()
                    if refund_obj:
                        logger.info("Script:: DAILY_REFUNDS_RAZORPAY:: Booking Id :%s Refund already exist" % booking_id)
                        continue

                if booking_invoice or proforma_invoice:
                    data = {
                        "tx_status": Payment.TX_STATUS_SUCCESS,
                        "tx_type": Payment.TX_TYPE_REFUND,
                        "vendor_status": "Refund",
                        "mode": Payment.PAYMENT_MODE_ONLINE,
                        "vendor": Payment.VENDOR_RAZOR_PAY,
                        "amount": amount_refunded,
                        "payment_vendor_id": rzrpay_refund_id,
                        "error_message": "Success",
                        "tx_data": "Created by System Script.",
                    }
                    if booking_invoice:
                        data["invoice"] = booking_invoice
                    elif proforma_invoice:
                        data["proforma_invoice"] = proforma_invoice

                    new_payment = Payment.objects.create(**data)
                    logger.info(
                        "Script:: DAILY_REFUNDS_RAZORPAY:: New refund created, id: {}".format(new_payment.id))
                else:
                    logger.error(
                        "Script:: DAILY_REFUNDS_RAZORPAY:: No Invoice Found: {}".format(booking_id))
        except:
            logger.exception("Script:: DAILY_REFUNDS_RAZORPAY:: Failed to get data from razor pay.")
        logger.info("Script:: DAILY_REFUNDS_RAZORPAY:: Script Ended - current_time: %s" % timezone.now())
