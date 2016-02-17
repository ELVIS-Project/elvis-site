#!/usr/bin/env bash

ENV="dev"
BASE_DIR="/srv/webapps/elvisdb"

# Save a backup
mv "${BASE_DIR}/${ENV}" "${BASE_DIR}/old/${ENV}_$(date +%s)"

# Clone the repo
git clone -b dev git@github.com:ELVIS-Project/elvis-database.git ${BASE_DIR}/${ENV}

# Set up the virtualenv
virtualenv -p python3 ${BASE_DIR}/${ENV}/.env

# Install requirements
source ${BASE_DIR}/${ENV}/.env/bin/activate
pip install -r ${BASE_DIR}/${ENV}/requirements.txt

# Perform Django management tasks
python ${BASE_DIR}/${ENV}/manage.py collectstatic --noinput
python ${BASE_DIR}/${ENV}/manage.py migrate --noinput

# Restart supervisor processes
sudo supervisorctl restart elvis-db-${ENV}
sudo supervisorctl restart elvis-celery-${ENV}

echo "Elvis DB ${ENV} Deployment Complete"