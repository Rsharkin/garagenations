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
    help = 'Script:: FRIDAY_PENDING_INVOICE_REPORT:: Daily Invoice report for previous day drops'

    def handle(self, *args, **options):
        current_time = timezone.now()
        logger.info("Script:: FRIDAY_PENDING_INVOICE_REPORT:: Script started - current_time: %s" % current_time)

        try:
            cur = connection.cursor()
            cur.execute('''select
                b.id as booking_id,
                bi.id as invoice_id,
                (case when bi.status=1 then 'Pending'
                    when bi.status=2 then 'Cancelled'
                    when bi.status=3 then 'Paid' end) as invoice_status,
                bs.status as booking_status,
                b.rework_booking_id,
                CONVERT_TZ(bi.created_at,'+00:00','+05:30') as invoice_creation_dt,
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
                bi.amt_wo_discount,
                bi.vat,
                bi.service_tax,
                bi.sb_tax,
                bi.kk_tax,
                (select sum(p.amount) from core_payment p where p.invoice_id=bi.id and tx_status=1) as total_payment,
                (select sum(bd.part_discount+bd.labour_discount+bd.material_discount)
                from core_bookingdiscount bd where bd.booking_id=b.id) as total_discount,
                bu.email,
                bu.phone,
                (select 1 from core_internalaccounts ia where ia.phone=bu.phone limit 1) as 'internal'
                from
                core_booking b
                inner join core_bumperuser bu on bu.id=b.user_id
                inner join core_bookingstatus bs on bs.id=b.status_id
                inner join core_bookinginvoice bi on bi.booking_id=b.id
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
                bi.status!=2 and b.actual_drop_time is null;''')
            rows = cur.fetchall()
            #num_fields = len(cur.description)
            field_names = [i[0] for i in cur.description]
            fp = open('/tmp/friday_pending_inv_report.csv', 'w')
            myFile = csv.writer(fp)
            myFile.writerow(field_names)
            myFile.writerows(rows)
            fp.close()
            fp = open('/tmp/friday_pending_inv_report.csv','r')
            attachment = {
                'content': base64.b64encode(fp.read()),
                'name': 'Friday Pending Invoices Report - ' + str(timezone.now().date()),
                'type': 'text/csv'
            }
            send_custom_notification('FINANCE_PENDING_INVOICE_REPORT', {'today_date':timezone.now().date()},
                                     attachments=[attachment])
        except:
            logger.exception("Script:: FRIDAY_PENDING_INVOICE_REPORT:: Failed to get data for yesterday invoice. CHECK QUERY!!")
        logger.info("Script:: FRIDAY_PENDING_INVOICE_REPORT:: Script ended")
