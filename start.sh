#!/usr/bin/env bash

virtualenv -p python3.6 venv
source ./venv/bin/activate
pip install -r requirements.txt

touch ./tornado_celery.conf
./script_fill.sh >> ./tornado_celery.conf
sudo cp ./tornado_celery.conf /etc/supervisor/conf.d/

# patching
cp file.patch ./venv/lib/python3.6/site-packages/tornado
cd ./venv/lib/python3.6/site-packages/tornado
patch -p0 < file.patch

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
