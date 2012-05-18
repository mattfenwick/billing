mysql -u root --batch -e 'select path from marks_billing.start_stop' > paths/raw/data.txt

python paths.py paths/raw/data.txt paths/cleaned/data.txt

mysql -u root < mysql/load_paths.sql