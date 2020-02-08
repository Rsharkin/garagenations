-- open_leads_at_end_everyday

DELIMITER $$
DROP procedure IF EXISTS open_leads_at_everyday_end$$
create procedure open_leads_at_everyday_end()
  BEGIN
    declare dt datetime;

    create temporary table foo (d date not null);

    set dt = '2016-05-17';
    while dt <= date(utc_timestamp()) do
      insert into foo (d) values (dt);
      set dt = date_add(dt, interval 1 day);
    end while;

    select
      f.d as 'the_date',
      count(bu.id) as 'Num_of_users_created',
      hot_warm_leads_on_given_date(f.d) as 'leads_at_end_day'
    from foo f
      left OUTER JOIN core_bumperuser bu
        on date(CONVERT_TZ(bu.date_joined, '+00:00', '+05:30')) = f.d
           and bu.phone is not null
           and bu.phone not in(select ia.phone from core_internalaccounts ia)

    group by f.d
    order by f.d asc
    ;

    drop temporary table foo;
  end $$
DELIMITER ;

-- call open_leads_at_everyday_end();