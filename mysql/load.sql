use marks_billing;

load data local infile 'data/cleaned/500.txt' into table staging;

load data local infile 'data/cleaned/600.txt' into table staging;

load data local infile 'data/cleaned/800.txt' into table staging;