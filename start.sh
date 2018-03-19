#!/usr/bin/env bash

# Database:
export NAME=highhopes
export USER=user
export PASSWORD=yourpassword
export HOST=127.0.0.1
export PORTDB=3307

mkdir logs

virtualenv -p python3.6 venv
source ./venv/bin/activate
pip install -r requirements.txt

sudo cp ./tornado_celery.conf /etc/supervisor/conf.d/

# patching
cp file.patch ./venv/lib/python3.6/site-packages/tornado
cd ./venv/lib/python3.6/site-packages/tornado
patch -p0 < file.patch


sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
