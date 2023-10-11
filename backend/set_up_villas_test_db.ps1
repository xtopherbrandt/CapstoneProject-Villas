dropdb -U xtopher villas-test
createdb -U xtopher villas-test
flask db upgrade
$env:CONFIG_FILE_NAME="env_test.json"
python .\insert_enum_data_in_db.py