# Inderjeet 24 Nov 2014
from django.conf import settings

# Types of view/grid in system
REPORT_BOOKING = 'report_booking'
REPORT_USER = 'report_user'
REPORT_NOTIFY_USER = 'report_notify_user'
REPORT_BOOKING_NOTIFICATIONS_SENT = 'report_booking_notifications_sent'
REPORT_USER_NOTIFICATIONS_SENT = 'report_user_notifications_sent'
REPORT_BOOKINGS_BY_USERS = 'report_booking_by_users'
REPORT_BOOKING_FOLLOWUPS = 'report_booking_followups'
REPORT_INQUIRY_FOLLOWUPS = 'report_inquiry_followups'
REPORT_BOOKING_HISTORY = 'report_booking_history'
REPORT_USER_INQUIRY = 'report_user_inquiry'
REPORT_BOOKING_IN_STATUS = 'report_booking_in_status'
REPORT_USER_INQUIRY_IN_STATUS = 'report_user_inquiry_in_status'
REPORT_WORKSHOP_LIVE = 'report_workshop_live'
REPORT_SUMMARY_PICKED = 'report_summary_picked'
REPORT_SUMMARY_TO_BE_PICKED = 'report_summary_to_be_picked'
REPORT_ALERTS_RAISED = 'report_alerts_raised'
REPORT_SCRATCH_FINDER_USERS = 'report_scratch_finder_users'
REPORT_SCRATCH_FINDER_LEADS = 'report_scratch_finder_leads'
REPORT_FEEDBACK_BY_CUSTOMER = 'report_feedback_by_customer'
REPORT_FEEDBACK_BY_OPS = 'report_feedback_by_ops'
REPORT_CREW_DASHBOARD_PICKUP = 'report_crew_dashboard_pickup'
REPORT_PART_DOCS = 'report_part_docs'

REPORT_TYPES = (
    (REPORT_BOOKING, REPORT_BOOKING),
    (REPORT_USER, REPORT_USER),
    (REPORT_BOOKINGS_BY_USERS, REPORT_BOOKINGS_BY_USERS),
    (REPORT_NOTIFY_USER, REPORT_NOTIFY_USER),
    (REPORT_BOOKING_NOTIFICATIONS_SENT, REPORT_BOOKING_NOTIFICATIONS_SENT),
    (REPORT_USER_NOTIFICATIONS_SENT, REPORT_USER_NOTIFICATIONS_SENT),
    (REPORT_BOOKING_FOLLOWUPS, REPORT_BOOKING_FOLLOWUPS),
    (REPORT_INQUIRY_FOLLOWUPS, REPORT_INQUIRY_FOLLOWUPS),
    (REPORT_BOOKING_HISTORY, REPORT_BOOKING_HISTORY),
    (REPORT_USER_INQUIRY, REPORT_USER_INQUIRY),
    (REPORT_BOOKING_IN_STATUS, REPORT_BOOKING_IN_STATUS),
    (REPORT_USER_INQUIRY_IN_STATUS, REPORT_USER_INQUIRY_IN_STATUS),
    (REPORT_WORKSHOP_LIVE, REPORT_WORKSHOP_LIVE),
    (REPORT_SUMMARY_PICKED, REPORT_SUMMARY_PICKED),
    (REPORT_SUMMARY_TO_BE_PICKED, REPORT_SUMMARY_TO_BE_PICKED),
    (REPORT_ALERTS_RAISED, REPORT_ALERTS_RAISED),
    (REPORT_SCRATCH_FINDER_USERS, REPORT_SCRATCH_FINDER_USERS),
    (REPORT_SCRATCH_FINDER_LEADS, REPORT_SCRATCH_FINDER_LEADS),
    (REPORT_FEEDBACK_BY_CUSTOMER, REPORT_FEEDBACK_BY_CUSTOMER),
    (REPORT_FEEDBACK_BY_OPS, REPORT_FEEDBACK_BY_OPS),
    (REPORT_CREW_DASHBOARD_PICKUP, REPORT_CREW_DASHBOARD_PICKUP),
    (REPORT_PART_DOCS, REPORT_PART_DOCS),
)

# Report booking
REPORT_BOOKING_MASTER_SQL_COLS = [
    'b.id',
    'b.status_id',
    'b.ops_status_id',
    "b.source ",
    "case b.lead_quality when 1 then 'Hot' when 4 then 'Red Hot' When 2 then 'Warm' When 3 then 'Cold' else b.lead_quality end as 'lead_quality' ",
    "bs.status_desc as 'status' ",
    "bss.ops_status_desc as 'ops_status' ",
    "CONCAT(bu.name,' ',bu.phone,' ',ifnull(bu.email,'') ) as 'user' ",
    "bu.id as 'user_id' ",
    "bu.name as 'name' ",
    "bu.phone as 'phone' ",
    "bu.email as 'email' ",
    "cm.name as 'model' ",
    "cb.name as 'brand' ",
    "w.name as 'workshop' ",
    "bu.utm_source as 'utm_source' ",
    "bu.utm_medium as 'utm_medium' ",
    "bu.utm_campaign as 'utm_campaign' ",
    "(select DATE_FORMAT(CONVERT_TZ(bu.date_joined,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'user_created_at' ",
    "case b.is_doorstep when 1 then 'Doorstep' else 'Pickup' end as 'is_doorstep' ",
    """
        (SELECT sum(CASE p.id
            WHEN 10 then 15
            WHEN 11 then 14
            WHEN 13 then 15
            WHEN 25 then 15
            WHEN 2 then
              (SELECT count(distinct(cp.id))
              FROM core_bookingpackagepanel bpp
              inner join core_carpanelprice cpp
                ON cpp.id=bpp.panel_id
              inner join core_carpanel cp
                ON cp.id=cpp.car_panel_id
                WHERE bpp.booking_package_id=bp.id)
            ELSE 0
        end) FROM core_bookingpackage bp inner join core_packageprice pp ON pp.id=bp.package_id
            inner join core_package p ON pp.package_id=p.id WHERE bp.booking_id=b.id) AS 'num_of_panels' """,
    "(select group_concat(p.name separator ', ') from core_bookingpackage bp inner join core_packageprice pp on bp.package_id=pp.id inner join core_package p on pp.package_id=p.id where b.id = bp.booking_id)  as 'packages' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.next_followup,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'next_followup' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'created_at' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.updated_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'updated_at' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.pickup_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'p_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.pickup_slot_end_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'p_time_end' ",
    "date(CONVERT_TZ(b.actual_pickup_time,'+00:00','+05:30')) as 'actual_pickup_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.drop_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'd_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.drop_slot_end_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'd_time_end' ",
    "bu1.name as 'assigned_to' ",
    """
        if((select 1 from core_bookingpackage bp inner join core_packageprice pp ON pp.id=bp.package_id
                inner join core_package p ON pp.package_id=p.id WHERE bp.booking_id=b.id and p.category=1
                limit 1), 1, 0)
            as 'has_vas_package'
    """,
    """
        (CASE
                    WHEN bs.flow_order_num<3 Then 'Cart'
                    WHEN (bs.flow_order_num>=3
                          AND b.status_id !=24
                          AND
                            (SELECT CONVERT_TZ(f.created_at,'+00:00','+05:30')
                             FROM bumper2.core_booking_followup bf
                             inner join bumper2.core_followup f
                               ON f.id=bf.followup_id
                             WHERE bf.booking_id=b.id
                             ORDER BY f.created_at LIMIT 1) is null ) Then 'PS'
                    WHEN (bs.flow_order_num>=3
                          AND b.status_id !=24
                          AND
                            (SELECT CONVERT_TZ(f.created_at,'+00:00','+05:30')
                             FROM bumper2.core_booking_followup bf
                             inner join bumper2.core_followup f
                               ON f.id=bf.followup_id
                             WHERE bf.booking_id=b.id
                             ORDER BY f.created_at LIMIT 1) >
                            (SELECT CONVERT_TZ(hb.updated_at,'+00:00','+05:30')
                             FROM bumper2.core_historicalbooking hb
                             WHERE hb.id=b.id
                               AND hb.status_id in (3,
                                                    26)
                             ORDER BY hb.updated_at LIMIT 1)) Then 'PS'
                    WHEN (b.status_id =24
                          AND
                            (SELECT 1
                             FROM bumper2.core_historicalbooking hb
                             WHERE hb.id=b.id
                               AND hb.status_id in (3,
                                                    26)
                             ORDER BY hb.updated_at LIMIT 1)
                          AND
                            (SELECT 1
                             FROM bumper2.core_booking_followup bf
                             inner join bumper2.core_followup f
                               ON f.id=bf.followup_id
                             WHERE bf.booking_id=b.id
                             ORDER BY f.created_at LIMIT 1) is null ) Then 'PS'
                    WHEN (b.status_id =24
                          AND
                            (SELECT CONVERT_TZ(f.created_at,'+00:00','+05:30')
                             FROM bumper2.core_booking_followup bf
                             inner join bumper2.core_followup f
                               ON f.id=bf.followup_id
                             WHERE bf.booking_id=b.id
                             ORDER BY f.created_at LIMIT 1) >
                            (SELECT CONVERT_TZ(hb.updated_at,'+00:00','+05:30')
                             FROM bumper2.core_historicalbooking hb
                             WHERE hb.id=b.id
                               AND hb.status_id in (3,
                                                    26)
                             ORDER BY hb.updated_at LIMIT 1)) Then 'PS'
                    ELSE 'Cart'
                END) AS 'created_in'
    """,
    """
       CASE
           WHEN
                  (SELECT 1
                   FROM bumper2.core_historicalbooking hb
                   WHERE hb.id=b.id
                     AND hb.updated_by_id=b.user_id
                   ORDER BY hb.id LIMIT 1) then 'User'
           ELSE 'Ops'
       END AS 'created_by'
    """,
    "b.rework_booking_id",
    "if((select 1 from core_bookingflag bf where bf.booking_id=b.id and bf.flag_type_id=1),1,0) as 'escalated_flag' ",
    "if((select 1 from core_bookingflag bf where bf.booking_id=b.id and bf.flag_type_id=2),1,0) as 'insurance_flag' ",
    "if(b.return_reason_id is null,0, 1) as 'car_returned' ",
    "(select buc.name from core_bumperuser buc where buc.id=b.caller_id) as 'caller' ",
    "b.city_id as 'city_id' "
]

REPORT_BOOKING_MASTER_SQL_WHERE_COLS_MAP = {
    'id': 'b.id',
    'status_id': 'b.status_id',
    'ops_status_id': 'b.ops_status_id',
    'city_id': 'b.city_id',
}

# Report booking
REPORT_BOOKING_HISTORY_MASTER_SQL_COLS = [
    'b.id',
    'b.status_id',
    'b.ops_status_id',
    "b.desc ",
    "b.source ",
    "b.latitude ",
    "b.longitude ",
    "bs.status_desc as 'status' ",
    "bss.ops_status_desc as 'ops_status' ",
    "CONCAT(bu.name,' ',bu.phone,' ',ifnull(bu.email,'') ) as 'user' ",
    "bu.id as 'user_id' ",
    "bu.name as 'name' ",
    "bu.phone as 'phone' ",
    "bu.email as 'email' ",
    "cm.name as 'model' ",
    "cb.name as 'brand' ",
    "w.name as 'workshop' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.next_followup,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'next_followup' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'created_at' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.updated_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'updated_at' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.pickup_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'p_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.pickup_slot_end_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'p_time_end' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.actual_pickup_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'e_p_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.drop_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'd_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.drop_slot_end_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'd_time_end' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.driver_arrived_drop_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'e_d_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.estimate_complete_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'cust_eta' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.workshop_eta,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'workshop_eta' ",
    "bu1.name as 'assigned_to' ",
    "bu2.name as 'updated_by' ",
    "(select buc.name from core_bumperuser buc where buc.id=b.caller_id) as 'caller' ",
]

REPORT_BOOKING_HISTORY_MASTER_SQL_WHERE_COLS_MAP = {
    'id': 'b.id',
    'status_id': 'b.status_id',
}

# Report Bookings by users
REPORT_BOOKINGS_BY_USERS_MASTER_SQL_COLS = [
    "count(DISTINCT( bu.id)) as 'users' ",
    "count(DISTINCT(b.id)) as 'bookings' ",
    "count(DISTINCT(If(b.status_id=15,b.id,NULL))) as 'cancelled' ",
    "count(DISTINCT(If(bs.flow_order_num>=8 and bs.id!=15,b.id,NULL))) as 'converted' ",
    "count(DISTINCT(If(b.status_id=16,b.id,NULL))) as 'closed' ",
    "(select DATE_FORMAT(CONVERT_TZ(bu.date_joined,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'user_join_dt' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'booking_dt' ",
    "bu.utm_source",
    "bu.utm_medium",
    "bu.utm_campaign",
    "bu.source"
]
REPORT_BOOKINGS_BY_USERS_MASTER_SQL_WHERE_COLS_MAP = {
    "user_join_dt": "bu.date_joined ",
    "booking_dt": "b.created_at ",
    "source": "bu.source ",
    "utm_source": "bu.utm_source ",
    "utm_medium": "bu.utm_medium ",
    "utm_campaign": "bu.utm_campaign "
}

# Report Users
REPORT_USER_MASTER_SQL_COLS = [
    "bu.id ",
    "bu.name ",
    "bu.phone ",
    "bu.email ",
    "bu.is_otp_validated ",
    "(select DATE_FORMAT(CONVERT_TZ(bu.date_joined,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'date_joined' ",
    "c.name as 'city' ",
    "cm.name as 'model' ",
    "count(distinct(b.id)) as 'bookings' ",
    "(select group_concat(b.id,',',bs.status_desc) from core_booking b, core_bookingstatus bs where b.user_id=bu.id and b.status_id=bs.id order by b.id desc limit 1) as 'latest_booking' ",
    "(select ui.id from core_userinquiry ui where ui.user_id=bu.id order by ui.id desc limit 1) as 'latest_inquiry' ",
    "IF(exists(select 1 from core_userdevices uds where uds.user_id=bu.id and uds.device_id is not null),1,0) as 'app_install' ",
    "bu.updated_at as 'updated_at' ",
    "bu.utm_source as 'utm_source' ",
    "bu.utm_medium as 'utm_medium' ",
    "bu.utm_campaign as 'utm_campaign' ",
    "bu.source"

]
REPORT_USER_MASTER_SQL_WHERE_COLS_MAP = {
    "date_joined": "bu.date_joined ",
    "utm_source": "bu.utm_source ",
    "utm_medium": "bu.utm_medium ",
    "utm_campaign": "bu.utm_campaign ",
    "source": "bu.source ",
}

#  List of users for notify-users screen
REPORT_NOTIFY_USER_MASTER_SQL_COLS = [
    "bu.id ",
    "bu.name ",
    "bu.phone ",
    "bu.email ",
    "bu.is_otp_validated ",
    "(select DATE_FORMAT(CONVERT_TZ(bu.date_joined,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'date_joined' ",
    "c.name as 'city' ",
    "cm.name as 'model' ",
    "count(distinct(b.id)) as 'bookings' ",
    "(select group_concat(b.id,',',bs.status_desc) from core_booking b, core_bookingstatus bs where b.user_id=bu.id and b.status_id=bs.id order by b.id desc limit 1) as 'latest_booking' ",
]
REPORT_NOTIFY_USER_MASTER_SQL_WHERE_COLS_MAP = {
    "date_joined": "bu.date_joined ",
}

#  List of message sent for a booking.
REPORT_BOOKING_NOTIFICATIONS_SENT_MASTER_SQL_COLS = [
    "m.id ",
    "m.booking_id ",
    "m.message_type ",
    "m.subject ",
    "m.message ",
    "m.message_send_level ",
    "m.direction ",
    "m.label ",
    "m.booking_id ",
    "m.action ",
    "m.notification_id",
    "m.sent_by_id",
    "bu1.name as 'sent_by' ",
    "(select DATE_FORMAT(CONVERT_TZ(m.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'created_at' ",
    " group_concat( mu.sent_to separator ', ') as 'sent_to'",
    "mu.gateway_api_response ",
    "mu.delivery_report ",
    "(select DATE_FORMAT(CONVERT_TZ(mu.delivered_dt,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as delivered_dt ",
    "(select DATE_FORMAT(CONVERT_TZ(mu.viewed_dt,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'viewed_dt' ",
    "mu.user_id ",
    "n.send_notice_to ",
]
REPORT_BOOKING_NOTIFICATIONS_SENT_MASTER_SQL_WHERE_COLS_MAP = {
    "booking_id": "m.booking_id ",
    "user_id": "mu.user_id ",
}

#  List of followups for all bookings.
REPORT_BOOKING_FOLLOWUPS_MASTER_SQL_COLS = [
    "f.id ",
    "bf.booking_id ",
    "f.updated_by_id ",
    "f.note ",
    "bu.name as 'updated_by' ",
    "bu1.name",
    "bu1.email",
    "bu1.phone",
    "(select DATE_FORMAT(CONVERT_TZ(f.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'created_at' ",
    "bs.status_desc as 'current_status' ",
    "b.city_id as 'city_id' ",
]
REPORT_BOOKING_FOLLOWUPS_MASTER_SQL_WHERE_COLS_MAP = {
    "booking_id": "bf.booking_id ",
    "updated_by_id": "f.updated_by_id ",
    "created_at": "f.created_at ",
    "city_id": "b.city_id ",
}

#  List of followups for all inquiries.
REPORT_INQUIRY_FOLLOWUPS_MASTER_SQL_COLS = [
    "f.id ",
    "ui.id as 'user_inquiry_id' ",
    "f.updated_by_id ",
    "f.note ",
    "bu.name as 'updated_by' ",
    "bu1.name",
    "bu1.email",
    "bu1.phone",
    "(select DATE_FORMAT(CONVERT_TZ(f.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'created_at' ",
    "ui.city_id as 'city_id' "
]
REPORT_INQUIRY_FOLLOWUPS_MASTER_SQL_WHERE_COLS_MAP = {
    "user_inquiry_id": "ui.id ",
    "updated_by_id": "f.updated_by_id ",
    "created_at": "f.created_at ",
    "city_id": "ui.city_id",
}

#  List of followups for all bookings.
REPORT_USER_INQUIRY_MASTER_SQL_COLS = [
    "ui.id ",
    "bu.id as  'user_id' ",
    "bu.name ",
    "bu.phone ",
    "bu.email ",
    "CONCAT(bu.name,' ',bu.phone,' ',ifnull(bu.email,'') ) as 'user' ",
    "concat(bu1.name,' ', bu1.ops_phone) as 'assigned_to' ",
    "ui.inquiry",
    "ui.status",
    "ui.source",
    "ui.utm_campaign",
    "ui.reference",
    "cm.name as 'model' ",
    "cb.name as 'brand' ",
    "case ui.lead_quality when 1 then 'Hot' when 4 then 'Red Hot' When 2 then 'Warm' When 3 then 'Cold' else ui.lead_quality end as 'lead_quality' ",
    "(select (select DATE_FORMAT(CONVERT_TZ(f.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) from core_userinquiry_followup uif inner join core_followup f on f.id=uif.followup_id where uif.userinquiry_id=ui.id order by created_at desc limit 1) as 'followup_created_at' ",
    "(select f.note from core_userinquiry_followup uif inner join core_followup f on f.id=uif.followup_id where uif.userinquiry_id=ui.id order by f.created_at desc limit 1) as 'last_followup_note' ",
    "(select (select DATE_FORMAT(CONVERT_TZ(f.next_followup_dt,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) from core_userinquiry_followup uif inner join core_followup f on f.id=uif.followup_id where uif.userinquiry_id=ui.id order by f.created_at desc limit 1) as 'next_followup_date' ",
    "(select b.id from core_booking b where b.user_id=ui.user_id order by b.id desc limit 1) as 'latest_booking'",
    "(select DATE_FORMAT(CONVERT_TZ(ui.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'created_at' ",
    "ui.city_id as 'city_id' "
]
REPORT_USER_INQUIRY_MASTER_SQL_WHERE_COLS_MAP = {
    'status': 'ui.status',
    'city_id': 'ui.city_id',
}

#  Booking Summary By Status
REPORT_BOOKING_IN_STATUS_MASTER_SQL_COLS = [
    "bs.status_desc ",
    "count(b.id) as 'num_of_bookings' ",
]
REPORT_BOOKING_IN_STATUS_MASTER_SQL_WHERE_COLS_MAP = {
}

#  Booking Summary By Status
REPORT_USER_INQUIRY_IN_STATUS_MASTER_SQL_COLS = [
    """
        case ui.status
            when 1 then 'Open'
            when 2 then 'Postponed'
            when 3 then 'Following Up'
            when 4 then 'Closed - Booking created'
            when 5 then 'RNR'
            when 6 then 'Closed - Booking not created'
            when 7 then 'Delayed Ops'
            else ''
        end as 'status' """,
    "count(ui.id) as 'num_of_inquiry' ",
]
REPORT_USER_INQUIRY_IN_STATUS_MASTER_SQL_WHERE_COLS_MAP = {
}

# Workshop Live Summary
REPORT_WORKSHOP_LIVE_MASTER_SQL_COLS = [
    "b.id as 'booking_id' ",
    "cm.name as 'car' ",
    "c.name as 'city' ",
    "b.city_id as 'city_id' ",
    """
    (SELECT sum(CASE p.id
                WHEN 10 then 15
                WHEN 11 then 14
                WHEN 13 then 15
                WHEN 25 then 15
                WHEN 2 then
                  (SELECT count(distinct(cp.id))
                  FROM core_bookingpackagepanel bpp
                  inner join core_carpanelprice cpp
                    ON cpp.id=bpp.panel_id
                  inner join core_carpanel cp
                    ON cp.id=cpp.car_panel_id
                    WHERE bpp.booking_package_id=bp.id 
                        and (not does_booking_has_full_body(b.id) or (does_booking_has_full_body(b.id) and cp.part_type=2)))
                ELSE 0
            end) 
            FROM core_bookingpackage bp 
            inner join core_packageprice pp ON pp.id=bp.package_id
            inner join core_package p ON pp.package_id=p.id 
            WHERE bp.booking_id=b.id) AS 'num_of_panels' """,
    """
       (SELECT sum(CASE p.id
                             WHEN 10 then 15
                             WHEN 11 then 14
                             WHEN 13 then 15
                             WHEN 25 then 15
                             WHEN 2 then
                                    (SELECT count(distinct(cp.id))
                                   FROM core_bookingpackagepanel bpp
                                   inner join core_carpanelprice cpp
                                     ON cpp.id=bpp.panel_id
                                   inner join core_carpanel cp
                                     ON cp.id=cpp.car_panel_id
                                     WHERE bpp.booking_package_id=bp.id
                                       AND cp.part_type=1
                                       AND not does_booking_has_full_body(b.id)
                                       AND cpp.type_of_work not in (3, 9))
                             ELSE 0
                         END)
              FROM core_bookingpackage bp
              inner join core_packageprice pp
                ON pp.id=bp.package_id
              inner join core_package p
                ON pp.package_id=p.id
                WHERE bp.booking_id=b.id) AS 'num_of_repair_panels'   
    """,
    """
        (SELECT sum(CASE p.id
                                     WHEN 2 then
                                            (SELECT count(distinct(cp.id))
                                           FROM core_bookingpackagepanel bpp
                                           inner join core_carpanelprice cpp
                                             ON cpp.id=bpp.panel_id
                                           inner join core_carpanel cp
                                             ON cp.id=cpp.car_panel_id
                                             WHERE bpp.booking_package_id=bp.id
                                               AND cp.part_type=1
                                               AND cpp.type_of_work in (3, 9))
                                     ELSE 0
                                 END)
                    FROM core_bookingpackage bp
                    inner join core_packageprice pp
                      ON pp.id=bp.package_id
                    inner join core_package p
                      ON pp.package_id=p.id
                      WHERE bp.booking_id=b.id) AS 'num_of_replace_panels'    
    """,
    """
        (SELECT sum(CASE p.id
                                     WHEN 2 then
                                            (SELECT count(distinct(cp.id))
                                           FROM core_bookingpackagepanel bpp
                                           inner join core_carpanelprice cpp
                                             ON cpp.id=bpp.panel_id
                                           inner join core_carpanel cp
                                             ON cp.id=cpp.car_panel_id
                                             WHERE bpp.booking_package_id=bp.id
                                               AND cp.part_type=2)
                                     ELSE 0
                                 END)
                    FROM core_bookingpackage bp
                    inner join core_packageprice pp
                      ON pp.id=bp.package_id
                    inner join core_package p
                      ON pp.package_id=p.id
                      WHERE bp.booking_id=b.id) AS 'num_of_spare'        
    """,
    "w.name AS 'workshop' ",
    """
        if((select 1 from core_bookingpackage bp inner join core_packageprice pp ON pp.id=bp.package_id
                inner join core_package p ON pp.package_id=p.id WHERE bp.booking_id=b.id and p.category=1
                limit 1), 1, 0)
            as 'has_vas_package'
    """,
    "(select DATE_FORMAT(CONVERT_TZ(b.actual_pickup_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) AS 'pickedUp_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.estimate_complete_time,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) AS 'customer_ETA' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.workshop_eta,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) AS 'workshop_ETA' ",
    """(
        select TIMESTAMPDIFF(HOUR, hb.updated_at, utc_timestamp)
        from core_historicalbooking hb where hb.id=b.id and hb.updated_by_id in (select bu1.id from core_bumperuser bu1
  inner join core_bumperuser_groups bug on bug.bumperuser_id=bu1.id where bug.group_id=13) order by hb.updated_at desc limit 1
    ) AS 'last_update_from_workshop' """,
    """
        (select if(count(distinct(hb.workshop_eta))>1,count(distinct(hb.workshop_eta)) - 1,null)
        from core_historicalbooking hb where hb.id=b.id) as "num_changes_workshop_eta"
    """,
    """
        (select if(count(distinct(hb.estimate_complete_time))>1,count(distinct(hb.estimate_complete_time)) - 1,null)
        from core_historicalbooking hb where hb.id=b.id) as "num_changes_customer_eta"
    """,
    """
        if((select 1 from core_historicalbooking hb
        where hb.id=b.id and hb.workshop_eta <=utc_timestamp limit 1),1,0) as 'workshop_eta_failed'
    """,
    """
        if((select 1 from core_historicalbooking hb
        where hb.id=b.id and hb.estimate_complete_time <=utc_timestamp limit 1),1,0) as 'customer_eta_failed'
    """,
    """
        if(bs.flow_order_num>=19 and (b.workshop_eta > utc_timestamp),1,0) as 'done_before_workshop_eta_failed'
    """,
    "bs.status_desc AS 'status' ",
    "bos.ops_status_desc AS 'ops_status' ",
    "bos.id AS 'ops_status_id' ",
    """
        if((select 1 from core_entitychangetracker ect
            where ect.content_id=b.id and ect.item_tracked='estimate_complete_time'
            and date(CONVERT_TZ(ect.created_at,'+00:00','+05:30')) = date(CONVERT_TZ(utc_timestamp(),'+00:00','+05:30')) limit 1), 1, null)
         AS 'is_eod_eta_done'
    """,
    """
        (select count(ect.id) from core_entitychangetracker ect
            where ect.content_id=b.id and ect.item_tracked='estimate_complete_time')
         AS 'num_eta_done'
    """,
    """
        datediff(if(bs.flow_order_num <15, date(CONVERT_TZ(utc_timestamp,'+00:00','+05:30')) ,(SELECT date(CONVERT_TZ(hb.updated_at,'+00:00','+05:30'))
                  FROM core_historicalbooking hb
                   inner join bumper2.core_bookingstatus hbs on hbs.id=hb.status_id
                   WHERE hb.id=b.id
                     AND hbs.flow_order_num >= 15
                   ORDER BY hb.updated_at LIMIT 1)),
            (SELECT date(CONVERT_TZ(hb.updated_at,'+00:00','+05:30'))
                  FROM core_historicalbooking hb
                   inner join bumper2.core_bookingstatus hbs on hbs.id=hb.status_id
                   WHERE hb.id=b.id
                     AND hbs.flow_order_num = 12
                   ORDER BY hb.updated_at LIMIT 1))
         AS 'total_eta_to_do'
    """,
    """
        if((select 1 from core_entitychangetracker ect
            where ect.content_id=b.id and ect.item_tracked='eod_message'
            and date(CONVERT_TZ(ect.created_at,'+00:00','+05:30')) = date(CONVERT_TZ(utc_timestamp(),'+00:00','+05:30')) limit 1),1 ,null)
         AS 'is_eod_message_done'
    """,
    """
        (select count(ect.id) from core_entitychangetracker ect
            where ect.content_id=b.id and ect.item_tracked='eod_message')
         AS 'num_eod_message_done'
    """,
    """
        datediff(if(bs.flow_order_num <21, date(CONVERT_TZ(utc_timestamp,'+00:00','+05:30')) ,(SELECT date(CONVERT_TZ(hb.updated_at,'+00:00','+05:30'))
                  FROM core_historicalbooking hb
                   inner join bumper2.core_bookingstatus hbs on hbs.id=hb.status_id
                   WHERE hb.id=b.id
                     AND hbs.flow_order_num >= 21
                   ORDER BY hb.updated_at LIMIT 1)),
            (SELECT date(CONVERT_TZ(hb.updated_at,'+00:00','+05:30'))
                  FROM core_historicalbooking hb
                   inner join bumper2.core_bookingstatus hbs on hbs.id=hb.status_id
                   WHERE hb.id=b.id
                     AND hbs.flow_order_num = 10
                   ORDER BY hb.updated_at LIMIT 1))
         AS 'total_eod_to_do'
    """,
    """
        if((b.rework_booking_id
        or (select 1 from core_bookingpackage bp where bp.booking_id=b.id and bp.rework=1 limit 1)
        or (select 1 from core_bookingpackage bp inner join core_bookingpackagepanel bpp on bpp.booking_package_id=bp.id where bp.booking_id=b.id and bpp.rework=1 limit 1))
        , 1,0) as 'rework'
    """,
    "buw.name as 'workshop_asst_mgr' ",
    "b.workshop_asst_mgr_id ",
    "if(date(CONVERT_TZ(b.estimate_complete_time,'+00:00','+05:30')) < date(CONVERT_TZ(b.workshop_eta,'+00:00','+05:30')),1,null) as 'ceta_less_weta' ",
]

REPORT_WORKSHOP_LIVE_MASTER_SQL_WHERE_COLS_MAP = {
    'city_id': 'b.city_id',
    'workshop_asst_mgr_id': 'b.workshop_asst_mgr_id',
}

# summary based on time frame.
REPORT_SUMMARY_PICKED_MASTER_SQL_COLS = [
    """
        sum((SELECT sum(CASE p.id
                      WHEN 10 then 15
                      WHEN 11 then 14
                      WHEN 13 then 15
                      WHEN 25 then 15
                      WHEN 2 then
                        (SELECT count(distinct(cp.id))
                         FROM core_bookingpackagepanel bpp
                           inner join core_carpanelprice cpp
                             ON cpp.id=bpp.panel_id
                           inner join core_carpanel cp
                             ON cp.id=cpp.car_panel_id
                         WHERE bpp.booking_package_id=bp.id)
                      ELSE 0
                      end) FROM core_bookingpackage bp inner join core_packageprice pp ON pp.id=bp.package_id
        inner join core_package p ON pp.package_id=p.id WHERE bp.booking_id=b.id)) AS 'num_of_panels'
    """,
    """
       sum((SELECT sum(CASE p.id
                             WHEN 10 then 15
                             WHEN 11 then 14
                             WHEN 13 then 15
                             WHEN 25 then 15
                             WHEN 2 then
                                    (SELECT count(distinct(cp.id))
                                   FROM core_bookingpackagepanel bpp
                                   inner join core_carpanelprice cpp
                                     ON cpp.id=bpp.panel_id
                                   inner join core_carpanel cp
                                     ON cp.id=cpp.car_panel_id
                                     WHERE bpp.booking_package_id=bp.id
                                       AND cp.part_type=1
                                       AND not does_booking_has_full_body(b.id)
                                       AND cpp.type_of_work not in (3, 9))
                             ELSE 0
                         END)
              FROM core_bookingpackage bp
              inner join core_packageprice pp
                ON pp.id=bp.package_id
              inner join core_package p
                ON pp.package_id=p.id
                WHERE bp.booking_id=b.id)) AS 'num_of_repair_panels'   
    """,
    """
        sum((SELECT sum(CASE p.id
                                     WHEN 2 then
                                            (SELECT count(distinct(cp.id))
                                           FROM core_bookingpackagepanel bpp
                                           inner join core_carpanelprice cpp
                                             ON cpp.id=bpp.panel_id
                                           inner join core_carpanel cp
                                             ON cp.id=cpp.car_panel_id
                                             WHERE bpp.booking_package_id=bp.id
                                               AND cp.part_type=1
                                               AND cpp.type_of_work in (3, 9))
                                     ELSE 0
                                 END)
                    FROM core_bookingpackage bp
                    inner join core_packageprice pp
                      ON pp.id=bp.package_id
                    inner join core_package p
                      ON pp.package_id=p.id
                      WHERE bp.booking_id=b.id)) AS 'num_of_replace_panels'    
    """,
    """
        sum((SELECT sum(CASE p.id
                                     WHEN 2 then
                                            (SELECT count(distinct(cp.id))
                                           FROM core_bookingpackagepanel bpp
                                           inner join core_carpanelprice cpp
                                             ON cpp.id=bpp.panel_id
                                           inner join core_carpanel cp
                                             ON cp.id=cpp.car_panel_id
                                             WHERE bpp.booking_package_id=bp.id
                                               AND cp.part_type=2)
                                     ELSE 0
                                 END)
                    FROM core_bookingpackage bp
                    inner join core_packageprice pp
                      ON pp.id=bp.package_id
                    inner join core_package p
                      ON pp.package_id=p.id
                      WHERE bp.booking_id=b.id)) AS 'num_of_spare'        
    """,
    "count(b.id) as 'num_of_cars' ",
    "b.actual_pickup_time as 'actual_pickup_time' ",
    "b.city_id as 'city_id' ",
]
REPORT_SUMMARY_PICKED_MASTER_SQL_WHERE_COLS_MAP = {
    "actual_pickup_time": "b.actual_pickup_time ",
    "city_id": "b.city_id ",
}

# summary based on time frame.
REPORT_SUMMARY_TO_BE_PICKED_MASTER_SQL_COLS = [
    """
        sum((SELECT sum(CASE p.id
                      WHEN 10 then 15
                      WHEN 11 then 14
                      WHEN 13 then 15
                      WHEN 25 then 15
                      WHEN 2 then
                        (SELECT count(distinct(cp.id))
                         FROM core_bookingpackagepanel bpp
                           inner join core_carpanelprice cpp
                             ON cpp.id=bpp.panel_id
                           inner join core_carpanel cp
                             ON cp.id=cpp.car_panel_id
                         WHERE bpp.booking_package_id=bp.id)
                      ELSE 0
                      end) FROM core_bookingpackage bp inner join core_packageprice pp ON pp.id=bp.package_id
        inner join core_package p ON pp.package_id=p.id WHERE bp.booking_id=b.id)) AS 'num_of_panels'
    """,
    "count(b.id) as 'num_of_cars' ",
    "b.pickup_time as 'pickup_time' ",
    "b.city_id as 'city_id' ",
]
REPORT_SUMMARY_TO_BE_PICKED_MASTER_SQL_WHERE_COLS_MAP = {
    "pickup_time": "b.pickup_time ",
    "city_id": "b.city_id ",
}

# summary based on time frame.
REPORT_ALERTS_RAISED_MASTER_SQL_COLS = [
    "ta.id ",
    "w.name as 'workshop_name' ",
    "CONCAT(bu.name,' ',bu.ops_phone) as 'raised_by' ",
    "tar.reason as 'alert_reason' ",
    "tar.reason_type as 'reason_type' ",
    "ta.reason_text as 'reason_text' ",
    "ta.resolved as 'resolved' ",
    "(select DATE_FORMAT(CONVERT_TZ(ta.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'raised_at' ",
]

REPORT_ALERTS_RAISED_MASTER_SQL_WHERE_COLS_MAP = {
    "resolved": "ta.resolved ",
}

# scratch finder users.
REPORT_SCRATCH_FINDER_USERS_MASTER_SQL_COLS = [
    "sfu.id ",
    "sfu.name ",
    "sfu.email ",
    "sfu.phone ",
    "sfu.utm_source",
    "sfu.utm_medium",
    "sfu.utm_campaign",
    "sfu.source",
    "(select count(sfl.id) from core_scratchfinderlead sfl where sfl.user_id=sfu.id) as 'referred' ",
    """
        (select count(distinct(b.id)) from core_booking b
            inner join core_bookingstatus bs on bs.id=b.status_id
            inner join core_bumperuser bu on bu.id=b.user_id and bs.flow_order_num >= 9 and bs.flow_order_num <= 24
            where bu.phone in (select sfl.phone from core_scratchfinderlead sfl where sfl.user_id=sfu.id))
        as 'converted'
    """,
    "(select DATE_FORMAT(CONVERT_TZ(sfu.date_joined,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'date_joined' ",
    "sfu.city_id as 'city_id' "
]

REPORT_SCRATCH_FINDER_USERS_MASTER_SQL_WHERE_COLS_MAP = {
    "date_joined": "sfu.date_joined ",
    "city_id": "sfu.city_id ",
}

# scratch finder leads.
REPORT_SCRATCH_FINDER_LEADS_MASTER_SQL_COLS = [
    "sfl.id ",
    "sfl.name ",
    "sfl.phone ",
    "bu.id as 'referrer_id' ",
    "bu.name as 'referrer_name' ",
    "bu.phone as 'referrer_phone' ",
    "sfl.detail",
    "sfl.status",
    "cm.name as 'model' ",
    "cb.name as 'brand' ",
    "bu1.name as 'updated_by' ",
    """ 
        (select group_concat(concat(b.id,'-',bs.status_desc)  separator '; ') 
            from core_bumperuser bu2 
            inner join core_booking b on b.user_id=bu2.id 
            inner join core_bookingstatus bs on b.status_id=bs.id 
            where bu2.phone = sfl.phone order by b.id desc) 
        as 'booking_status' 
    """,
    """ 
        (select group_concat(concat(ui.id,'-',
                CASE ui.status
                    when 1 then 'Open'
                    when 2 then 'Postponed'
                    when 3 then 'Following Up'
                    when 4 then 'Closed - Booking created'
                    when 5 then 'RNR'
                    when 6 then 'Closed - Booking not created'
                    when 7 then 'Delayed Ops'
                    when 8 then 'Duplicate'
                    when 9 then 'Closed - Booking created before followup'
                    when 10 then 'Closed - Price Issue'
                    when 11 then 'Closed - Closed - Trust Issue'
                    else ui.status
                 END)  separator '; ') 
            from core_bumperuser bu2 
            inner join core_userinquiry ui on ui.user_id=bu2.id 
            where bu2.phone = sfl.phone order by ui.id desc) 
        as 'inquiry_status' 
    """,
    "(select DATE_FORMAT(CONVERT_TZ(sfl.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'created_at' ",
    "CONCAT('https://" + settings.BOTO_S3_BUCKET_BOOKING + ".s3.amazonaws.com/', m.file) as 'media_url' ",
    "bu.city_id as 'city_id'",
]

REPORT_SCRATCH_FINDER_LEADS_MASTER_SQL_WHERE_COLS_MAP = {
    "created_at": "sfl.created_at ",
    "city_id": "bu.city_id ",
}

# Feedback submitted by user in app
REPORT_FEEDBACK_BY_CUSTOMER_MASTER_SQL_COLS = [
    "bcf.booking_id ",
    "bcf.booking_experience ",
    "bcf.customer_care ",
    "bcf.work_quality ",
    "bcf.value_for_money ",
    "bcf.pickup_experience ",
    "bcf.any_suggestions ",
    "bu.phone ",
    "(select DATE_FORMAT(CONVERT_TZ(bcf.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'created_at' ",
    "b.city_id as 'city_id' "
]

REPORT_FEEDBACK_BY_CUSTOMER_MASTER_SQL_WHERE_COLS_MAP = {
    "created_at": "bcf.created_at ",
    "city_id": "b.city_id ",
}

# Feedback submitted by ops on behalf of user.
REPORT_FEEDBACK_BY_OPS_MASTER_SQL_COLS = [
    "bf.booking_id ",
    "bf.bumper_app ",
    "bf.experience_rating ",
    "bf.customer_care ",
    "bf.work_quality ",
    "bf.value_for_money ",
    "bf.pick_drop_service ",
    "bf.wow_moment ",
    "bf.any_suggestions ",
    "bf.feedback_remarks ",
    "bf.customer_issue ",
    "bf.customer_relation_remarks ",
    "bf.referrals ",
    "bu.phone ",
    "(select DATE_FORMAT(CONVERT_TZ(bf.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'created_at' ",
    "b.city_id as 'city_id' ",
]

REPORT_FEEDBACK_BY_OPS_MASTER_SQL_WHERE_COLS_MAP = {
    "created_at": "bf.created_at ",
    "city_id": "b.city_id ",
}

# For crew dashboard for pickup data
REPORT_CREW_DASHBOARD_PICKUP_MASTER_SQL_COLS = [
    "b.id AS 'booking_id' ",
    "b.status_id AS 'status_id' ",
    "bs.status_desc AS 'status' ",
    "bs.flow_order_num AS 'flow_order_num' ",
    "b.ops_status_id AS 'ops_status_id' ",
    "bos.ops_status_desc AS 'ops_status' ",
    "w.name as 'workshop' ",
    "date(CONVERT_TZ(b.pickup_time,'+00:00','+05:30')) AS 'pickup_date' ",
    "date(CONVERT_TZ(b.drop_time,'+00:00','+05:30')) AS 'drop_date' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.pickup_time,'+00:00','+05:30'), '%%H:%%i')) AS 'pickup_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.pickup_slot_end_time,'+00:00','+05:30'), '%%H:%%i')) AS 'pickup_slot_end_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.actual_pickup_time,'+00:00','+05:30'), '%%H:%%i')) AS 'car_picked_at_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.workshop_reached_time,'+00:00','+05:30'), '%%H:%%i')) AS 'workshop_reached_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.drop_time,'+00:00','+05:30'), '%%H:%%i')) AS 'drop_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.drop_slot_end_time,'+00:00','+05:30'), '%%H:%%i')) AS 'drop_slot_end_time' ",
    "(select DATE_FORMAT(CONVERT_TZ(b.actual_drop_time,'+00:00','+05:30'), '%%H:%%i')) AS 'car_delivered_time' ",
    "bup.id as 'pickup_driver_id' ",
    "bup.name as 'pickup_driver' ",
    "bud.id as 'drop_driver_id' ",
    "bud.name as 'drop_driver' ",
    "ap.address1 ",
    "ap.address2",
    "ap.city",
    "ap.latitude",
    "ap.longitude",
    "ad.address1 as 'drop_address1' ",
    "ad.address2 as 'drop_address2' ",
    "ad.city as 'drop_city' ",
    "ad.latitude as 'drop_latitude' ",
    "ad.longitude as 'drop_longitude' ",
    "b.city_id as 'city_id' ",
]

REPORT_CREW_DASHBOARD_PICKUP_MASTER_SQL_WHERE_COLS_MAP = {
    "actual_pickup_time": "b.actual_pickup_time ",
    "pickup_time": "b.pickup_time ",
    "drop_time": "b.drop_time ",
    "city_id": "b.city_id ",
}

# For part documents/requests
REPORT_PART_DOCS_MASTER_SQL_COLS = [
    "bpd.id",
    "b.id AS 'booking_id' ",
    "cp.name as 'panel_name' ",
    "cm.name as 'car_model' ",
    "cb.name as 'car_brand' ",
    "uc.registration_number as 'car_reg_num' ",
    "uc.purchased_on as 'car_purchased_on' ",
    "uc.year as 'car_year_of_manufacture' ",
    "cmv.name as 'car_variant' ",
    "bpd.quote_eta ",
    "bpd.status_id ",
    "pds.name as 'doc_status' ",
    "c.name as 'city' ",
    "b.city_id as 'city_id' ",
    "(select DATE_FORMAT(CONVERT_TZ(bpd.created_at,'+00:00','+05:30'), '%%Y-%%m-%%d %%H:%%i')) as 'created_at' ",
]

REPORT_PART_DOCS_MASTER_SQL_WHERE_COLS_MAP = {
    "city_id": "b.city_id ",
}
