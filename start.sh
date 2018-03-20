#!/usr/bin/env bash

# Database:
export NAME=
export USER=
export PASSWORD=
export HOST=
export PORTDB=

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
