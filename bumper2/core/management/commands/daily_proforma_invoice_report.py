"""
Daily Proforma Invoice report for Rohan/Khaja.
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
    help = 'Script:: DAILY_PROFORMA_INVOICE_REPORT:: Daily Invoice report for previous day drops'

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: DAILY_PROFORMA_INVOICE_REPORT:: Script started - current_time: %s" % current_time)

        try:
            cur = connection.cursor()
            cur.execute('''select
                b.id as booking_id,
                concat("P", bi.id) as proforma_invoice_id,
                bs.status,
                b.rework_booking_id,
                CONVERT_TZ(bi.created_at,'+00:00','+05:30') as proforma_invoice_creation_dt,
                CONVERT_TZ(bi.updated_at,'+00:00','+05:30') as proforma_invoice_updated_dt,
                p.name as package_name,
                cp.name as panel_name,
                cpp.type_of_work,
                cp.part_type,
                w.name as workshop_name,
                CONVERT_TZ(b.actual_pickup_time,'+00:00','+05:30') as actual_pickup_dt,
                CONVERT_TZ(b.actual_drop_time,'+00:00','+05:30') as actual_drop_dt,
                cm.name as car_model_name,
                uc.registration_number,
                cm.car_type,
                bi.payable_amt,
                (select sum(p.amount) from core_payment p where p.proforma_invoice_id=bi.id and tx_status=1) as total_payment,
                bu.email,
                bu.phone,
                (select 1 from core_internalaccounts ia where ia.phone=bu.phone limit 1) as 'internal'
                from
                core_booking b
                inner join core_bumperuser bu on bu.id=b.user_id
                inner join core_bookingstatus bs on bs.id=b.status_id
                inner join core_bookingproformainvoice bi on bi.booking_id=b.id
                inner join core_usercar uc on uc.id=b.usercar_id
                inner join core_carmodel cm on cm.id=uc.car_model_id
                inner join core_bookingpackage bp on bp.booking_id=b.id
                inner join core_packageprice pp on pp.id=bp.package_id
                inner join core_package p on p.id=pp.package_id
                left join core_bookingpackagepanel bpp on bpp.booking_package_id=bp.id
                left join core_carpanelprice cpp on cpp.id=bpp.panel_id
                left join core_carpanel cp on cp.id=cpp.car_panel_id
                left join core_workshop w on w.id=b.workshop_id
                where
                date(CONVERT_TZ(bi.updated_at,
                '+00:00','+05:30')) = date(subdate(CONVERT_TZ(now(),'+00:00','+05:30'),1));''')
            rows = cur.fetchall()
            #num_fields = len(cur.description)
            field_names = [i[0] for i in cur.description]
            fp = open('/tmp/today_proforma_invoice_report.csv', 'w')
            myFile = csv.writer(fp)
            myFile.writerow(field_names)
            myFile.writerows(rows)
            fp.close()
            fp = open('/tmp/today_proforma_invoice_report.csv','r')
            attachment = {
                'content': base64.b64encode(fp.read()),
                'name': 'Daily Invoice Report - ' + str(timezone.now().date()),
                'type': 'text/csv'
            }
            send_custom_notification('FIN_DAILY_PROFORMA_INV_REPORT', {'today_date':timezone.now().date()},
                                     attachments=[attachment])
        except:
            logger.exception("Script:: DAILY_PROFORMA_INVOICE_REPORT:: Failed to get data for yesterday invoice. CHECK QUERY!!")
        logger.info("Script:: DAILY_PROFORMA_INVOICE_REPORT:: Script ended")
