use marks_billing;




-- ----------------------------------------------------------------------------
-- story 1:  ignore paths in /home/vnmr/vnmrsys/gshimlib/* or
--              /home/vnmr/vnmrsys/exp*

create view ignored_path as (
  select
    id, 
    path, 
    time, 
    isstart
  from event 
  where path regexp '(/vnmrsys/gshimlib/|/vnmrsys/exp|/vnmrj_3\.2_A|/vnmrj_2\.3_A|BioPack\.dir)'
);


-- ----------------------------------------------------------------------------
-- story 2:  report paths that aren't ignored and have either less than 2
--             or more than 2 associated events

create view v_wrong_number_of_events as (
  select 
    e.path, 
    count(*) as `count`
  from event e 
  where e.path NOT regexp '(/vnmrsys/gshimlib/|/vnmrsys/exp|/vnmrj_3\.2_A|/vnmrj_2\.3_A|BioPack\.dir)'
  group by e.path 
  having count(*) != 2
);


create view wrong_number_of_events as (
  select 
    e1.id, 
    e1.path,
    e1.time,
    e1.isstart, 
    e2.`count`
  from event e1 
  inner join v_wrong_number_of_events e2
  on e1.path = e2.path
);

-- ----------------------------------------------------------------------------
-- story 3:  report paths for which there are 2 associated events,
--             but either both are starts or both are stops

create view two_starts_or_two_stops as (
  select 
    e1.id       as startid,
    e2.id       as endid,
    e1.path     as path,
    e1.time     as starttime,
    e2.time     as endtime,
    timediff(e2.time, e1.time)
                as elapsedtime,
    e1.isstart  as `status1`,
    e2.isstart  as `status2`
  from event e1 
  inner join event e2 
    on e1.path = e2.path AND
    e1.isstart = e2.isstart AND
    e1.id != e2.id
  where e1.path NOT regexp '(/vnmrsys/gshimlib/|/vnmrsys/exp|/vnmrj_3\.2_A|/vnmrj_2\.3_A|BioPack\.dir)'
);

-- ----------------------------------------------------------------------------
-- story 4:  paths for which there are exactly 2 associated events,
--             and one is a start, and the other is a stop


create view v_of_interest as (
  select 
    e.id,
    e.path,
    e.time,
    e.isstart
  from event e
  left join ignored_path i
    on e.id = i.id -- AND i.id is null
  left join wrong_number_of_events w
    on e.id = w.id -- AND w.id is null
  left join two_starts_or_two_stops t
    on e.id = t.startid -- AND t.startid is null
  where i.id is null and w.id is null and t.startid is null
);


create view start_stop as (
  select 
    e1.id   as startid,
    e2.id   as endid,
    e1.path as path,
    e1.time as starttime,
    e2.time as endtime,
    timediff(e2.time, e1.time) as elapsedtime
  from v_of_interest e1 
  inner join v_of_interest e2 
    on e1.path = e2.path
  where e1.isstart and not e2.isstart
);


-- ----------------------------------------------------------------------------
-- sanity checks:  
--   1. sum of ignored + too many/too few + 2 starts/2 stops + of interest = total events

create view v_totals as (
  select
    (select count(*) from two_starts_or_two_stops) as two, 
    (select count(*) from wrong_number_of_events) as wrong,
    (select count(*) from ignored_path) as ignored, 
    (select count(*) from v_of_interest) as interesting
);


create view sanity_event_totals as (
  select 
    two + wrong + ignored + interesting as a, 
  (select count(*) from event) b,
  interesting c,
  (select count(*) from start_stop) d -- should be 1/2 c
  from v_totals
);


create view elapsed_2012 as (
  select * 
  from start_stop 
  where year(starttime) = 2012 
  order by starttime asc
);
