-- week start date.

DELIMITER $$
DROP FUNCTION IF EXISTS get_week_start_date$$
CREATE FUNCTION get_week_start_date (given_date date)
  RETURNS date
DETERMINISTIC
  BEGIN
    return (CASE
           WHEN dayofweek(CONVERT_TZ(given_date,'+00:00','+05:30')) != 1
             then date(CONVERT_TZ(given_date,'+00:00','+05:30') - interval (DAYOFWEEK(CONVERT_TZ(given_date,'+00:00','+05:30'))-1) day)
           ELSE date(CONVERT_TZ(given_date,'+00:00','+05:30'))
       END);
  END$$
DELIMITER ;