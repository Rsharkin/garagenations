"""
Daily Invoice Payment Mismatch report to Ashvin/Anuj
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from core.managers.generalManager import send_custom_notification
import csv
import base64
import logging
logger = logging.getLogger('bumper.scripts')


class Command(BaseCommand):
    can_import_settings = True
    help = 'Script:: INVOICE_PAYMENT_MISMATCH_REPORT:: Invoice Payment mismatch report - for closed bookings only.'

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: INVOICE_PAYMENT_MISMATCH_REPORT:: Script started - current_time: %s" % current_time)

        try:
            cur = connection.cursor()
            cur.execute('''
            select b.id as booking_id, bi.payable_amt, bi.amt_wo_discount,
            (select sum(amount) from core_payment p where p.tx_status=1 and p.tx_type=1 and p.invoice_id=bi.id) as paid_amt,
            (select sum(amount) from core_payment p where p.tx_status=1 and p.tx_type=2 and p.invoice_id=bi.id) as refund_amt
            from core_booking b
            inner join core_bookinginvoice bi on bi.booking_id = b.id
            where b.status_id in (22,23) and bi.status!=2
            and bi.payable_amt != (select sum(amount) from core_payment p where p.tx_status=1 and p.tx_type=1 and p.invoice_id=bi.id);
            ''')
            rows = cur.fetchall()
            #num_fields = len(cur.description)
            field_names = [i[0] for i in cur.description]
            fp = open('/tmp/inv_pay_mismatch_report.csv', 'w')
            myFile = csv.writer(fp)
            myFile.writerow(field_names)
            myFile.writerows(rows)
            fp.close()
            fp = open('/tmp/inv_pay_mismatch_report.csv','r')
            attachment = {
                'content': base64.b64encode(fp.read()),
                'name': 'Invoice Payment Mismatch Report - ' + str(timezone.now().date()),
                'type': 'text/csv'
            }
            send_custom_notification('INVOICE_PAYMENT_MISMATCH', {'today_date':timezone.now().date()},
                                     attachments=[attachment])
        except:
            logger.exception("Script:: INVOICE_PAYMENT_MISMATCH_REPORT:: Failed to get data for yesterday invoice. CHECK QUERY!!")
        logger.info("Script:: INVOICE_PAYMENT_MISMATCH_REPORT:: Script ended")
