use marks_billing;

-- note that these command expect to be run from a certain folder
--   the root folder of the project
load data local infile 'data/cleaned/500.txt' into table staging;

load data local infile 'data/cleaned/600.txt' into table staging;

load data local infile 'data/cleaned/800.txt' into table staging;