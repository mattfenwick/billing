use marks_billing;

insert into experiment (path) select distinct path from staging;

insert into event (path, time, isstart) 
  select 
    path, 
    concat(year, '-', month, '-', day, ' ', hour, ':', minute, ':', second), 
    case when 
      status = 'Experiment started' then 1 
      when status = "Acquisition complete" then 0 
    end 
  from staging;