"""
Daily Drop report for Rohan/Khaja.
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
    help = 'Script:: FINANCE_PAYMENT_REPORT:: Daily Payment report for previous day payments'

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: FINANCE_PAYMENT_REPORT:: Script started - current_time: %s" % current_time)

        try:
            cur = connection.cursor()
            cur.execute('''select
                b.id as booking_id,
                bs.status,
                bi.id as invoice_id,
                p.id as payment_id,
                p.vendor,
                p.mode,
                w.name as workshop_name,
                driver.name as driver_name,
                CONVERT_TZ(b.actual_pickup_time,'+00:00','+05:30') as actual_pickup_dt,
                CONVERT_TZ(b.actual_drop_time,'+00:00','+05:30') as actual_drop_dt,
                CONVERT_TZ(p.updated_at,'+00:00','+05:30') as payment_dt,
                cm.name as car_model_name,
                uc.registration_number,
                cm.car_type,
                bi.payable_amt,
                (select group_concat(p.name) from core_bookingpackage bp
                inner join core_packageprice pp on pp.id=bp.package_id
                inner join core_package p on p.id=pp.package_id
                where bp.booking_id=b.id) as package_names,
                (select group_concat(DISTINCT CONCAT(cp.name,' - ',cpp.type_of_work)
                  SEPARATOR ',') from
                core_bookingpackage bp
                left join core_bookingpackagepanel bpp on bpp.booking_package_id=bp.id
                left join core_carpanelprice cpp on cpp.id=bpp.panel_id
                left join core_carpanel cp on cp.id=cpp.car_panel_id
                where bp.booking_id=b.id) as panels,
                p.amount as paid_amt,
                (select sum(bd.part_discount+bd.labour_discount+bd.material_discount)
                from core_bookingdiscount bd where bd.booking_id=b.id) as total_discount
                from
                core_booking b
                inner join core_bookingstatus bs on bs.id=b.status_id
                inner join core_bookinginvoice bi on bi.booking_id=b.id
                inner join core_payment p on p.invoice_id=bi.id
                inner join core_usercar uc on uc.id=b.usercar_id
                inner join core_carmodel cm on cm.id=uc.car_model_id
                left join core_workshop w on w.id=b.workshop_id
                left join core_bumperuser driver on driver.id=b.drop_driver_id
                where p.tx_status=1
                and date(CONVERT_TZ(p.updated_at,'+00:00','+05:30')) = date(subdate(CONVERT_TZ(now(),'+00:00','+05:30'),1));''')
            rows = cur.fetchall()
            num_fields = len(cur.description)
            field_names = [i[0] for i in cur.description]
            fp = open('/tmp/today_payment_report.csv', 'w')
            myFile = csv.writer(fp)
            myFile.writerow(field_names)
            myFile.writerows(rows)
            fp.close()
            fp = open('/tmp/today_payment_report.csv','r')
            attachment = {
                'content': base64.b64encode(fp.read()),
                'name': 'Payment Report - ' + str(timezone.now().date()),
                'type': 'text/csv'
            }
            send_custom_notification('FINANCE_PAYMENT_REPORT', {'today_date':timezone.now().date()},
                                     attachments=[attachment])
        except:
            logger.exception("Script:: FINANCE_PAYMENT_REPORT:: Failed to get data for yesterday payments. CHECK QUERY!!")
        logger.info("Script:: FINANCE_PAYMENT_REPORT:: Script ended")
