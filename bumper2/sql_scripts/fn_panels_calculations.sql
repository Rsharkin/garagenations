-- does_booking_has_full_body
DELIMITER $$
DROP FUNCTION IF EXISTS does_booking_has_full_body$$
CREATE FUNCTION does_booking_has_full_body (booking_id int)
  RETURNS INT
DETERMINISTIC
  BEGIN
    return if((SELECT 1
            FROM core_bookingpackage bp
              inner join core_packageprice pp
                ON pp.id=bp.package_id
              inner join core_package p
                ON pp.package_id=p.id
            WHERE bp.booking_id=booking_id and p.category=3),1,0);
  END$$
DELIMITER ;


-- num_of_panels
DELIMITER $$
DROP FUNCTION IF EXISTS num_of_panels$$
CREATE FUNCTION num_of_panels (booking_id int)
  RETURNS INT
DETERMINISTIC
  BEGIN
    DECLARE does_booking_has_full_body BOOL;
    set does_booking_has_full_body = does_booking_has_full_body(booking_id);

    return (SELECT sum(CASE p.id
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
                                and (not does_booking_has_full_body or (does_booking_has_full_body and cp.part_type=2)))
                       ELSE 0
                       END)
            FROM
              core_booking b
              inner join core_bookingpackage bp
                ON bp.booking_id = b.id
              inner join core_packageprice pp
                ON pp.id=bp.package_id
              inner join core_package p
                ON pp.package_id=p.id
            WHERE bp.booking_id=booking_id and b.return_reason_id is null and b.rework_booking_id is null);
  END$$
DELIMITER ;