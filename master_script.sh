#!/bin/bash

# parse ARC5 file data
echo
echo "#############"
echo "NETWORK "
echo "#############"
echo

echo
echo "PARSE DATA FROM FILE "
echo "#############"
echo
cd arc5-parser
. venv/bin/activate
# pip install -r requirements.txt
python parse_partenaires.py
python parse_subventions.py
python parse_dashboard.py
deactivate
cd ..

# parse ARCs DB and merge into single mongo collection
echo
echo "PARSE ARC DATABASE "
echo "#############"
echo
cd wp-api-crawler
node app.js
cd ..

# export mongo collection to CSV
cd mongoexport
sh export_to_csv.sh
cd ..

# clean the data (remove duplicate, etc)
cd matrix
. venv/bin/activate
python matrix.py
deactivate
cd ..

echo
echo "#############"
echo "QUESTIONNAIRE "
echo "#############"
echo

cd reponsesBrut
python parse.py
cd ..
