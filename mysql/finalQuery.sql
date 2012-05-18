select 
  path, 
  seconds,
  seconds / 60 as minutes,
  seconds / 3600 as hours 
from (
  select 
    i.path, 
    sum(time_to_sec(elapsedtime)) as seconds 
  from interesting_paths i 
  inner join start_stop s 
    on s.path regexp i.path 
  where year(starttime) = 2012 and month(starttime) between 1 and 4
  group by i.path
) q;