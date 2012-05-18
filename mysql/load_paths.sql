use marks_billing;

-- note that these command expect to be run from a certain folder
--   the root folder of the project
load data local infile 'paths/cleaned/data.txt' into table interesting_paths (path);