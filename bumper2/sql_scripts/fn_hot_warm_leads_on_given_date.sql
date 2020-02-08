-- status on a given date, where more updates to booking exists.

DELIMITER $$
DROP FUNCTION IF EXISTS hot_warm_leads_on_given_date$$
CREATE FUNCTION hot_warm_leads_on_given_date (given_date date)
  RETURNS Int
DETERMINISTIC
  BEGIN
    return (select
              count(DISTINCT(booking_id)) as 'num_of_leads'
            from (SELECT
                    b.id as 'booking_id',
                    date(CONVERT_TZ(b.created_at, '+00:00', '+05:30'))    AS 'booking_dt',
                    -- below select data does not matter
                    ''                                             AS 'timestamp_taken',
                    ''                                             AS 'next_followup_at_that_time',
                    ''                                             AS 'status_at_that_time',
                    ''                                             AS 'lead_quality_at_that_time'
                  FROM core_booking b
                    inner join core_bumperuser bu on bu.id = b.user_id
                  WHERE
                    bu.phone is not null
                    and not exists(select 1 from core_internalaccounts ia where ia.phone=bu.phone)
                    and date(CONVERT_TZ(b.updated_at, '+00:00', '+05:30')) > given_date
                    AND (SELECT hb.status_id
                         FROM core_historicalbooking hb
                         WHERE hb.id = b.id
                               AND date(CONVERT_TZ(hb.updated_at, '+00:00', '+05:30')) <= given_date
                         ORDER BY CONVERT_TZ(hb.updated_at, '+00:00', '+05:30') DESC
                         LIMIT 1) IN (1, 2, 3, 26)
                    AND ((SELECT hb.lead_quality
                          FROM core_historicalbooking hb
                          WHERE hb.id = b.id
                                AND date(CONVERT_TZ(hb.updated_at, '+00:00', '+05:30')) <= given_date
                          ORDER BY CONVERT_TZ(hb.updated_at, '+00:00', '+05:30') DESC
                          LIMIT 1) is NULL
                         OR
                         (SELECT hb.lead_quality
                          FROM core_historicalbooking hb
                          WHERE hb.id = b.id
                                AND date(CONVERT_TZ(hb.updated_at, '+00:00', '+05:30')) <= given_date
                          ORDER BY CONVERT_TZ(hb.updated_at, '+00:00', '+05:30') DESC
                          LIMIT 1) in (1,2,4) )
                    AND ((SELECT date(CONVERT_TZ(hb.next_followup, '+00:00', '+05:30'))
                          FROM core_historicalbooking hb
                          WHERE hb.id = b.id
                                AND date(CONVERT_TZ(hb.updated_at, '+00:00', '+05:30')) <= given_date
                          ORDER BY CONVERT_TZ(hb.updated_at, '+00:00', '+05:30') DESC
                          LIMIT 1) IS NULL
                         OR
                         (SELECT date(CONVERT_TZ(hb.next_followup, '+00:00', '+05:30'))
                          FROM core_historicalbooking hb
                          WHERE hb.id = b.id
                                AND date(CONVERT_TZ(hb.updated_at, '+00:00', '+05:30')) <= given_date
                          ORDER BY CONVERT_TZ(hb.updated_at, '+00:00', '+05:30') DESC
                          LIMIT 1) < given_date + INTERVAL 1 WEEK)

                  UNION
                  -- status on a given date, where more updates to booking exists.
                  SELECT
                    b.id as 'booking_id',
                    date(CONVERT_TZ(b.created_at, '+00:00', '+05:30'))    AS 'booking_dt',
                    date(CONVERT_TZ(b.updated_at, '+00:00', '+05:30'))    AS 'timestamp_taken',
                    date(CONVERT_TZ(b.next_followup, '+00:00', '+05:30')) AS 'next_followup_at_that_time',
                    b.status_id AS 'status_at_that_time',
                    b.lead_quality as 'lead_quality_at_that_time'
                  FROM core_booking b
                    inner join core_bumperuser bu on bu.id=b.user_id
                  WHERE
                    bu.phone is not null
                    and not exists(select 1 from core_internalaccounts ia where ia.phone=bu.phone)
                    and date(CONVERT_TZ(b.updated_at, '+00:00', '+05:30')) <= given_date
                    AND b.status_id IN (1, 2, 3, 26)
                    AND (b.next_followup IS NULL OR b.next_followup <= given_date + INTERVAL 1 WEEK)
                    AND (b.lead_quality IS NULL OR b.lead_quality in (1,2,4))
                 ) as C);
  END$$
DELIMITER ;