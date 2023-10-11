dropdb -U xtopher villas
createdb -U xtopher villas
flask db upgrade
$env:CONFIG_FILE_NAME="env_local.json"
python .\insert_enum_data_in_db.py