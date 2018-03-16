#!/usr/bin/env bash

virtualenv -p python3.6 venv

source ./venv/bin/activate

pip install -r requirements.txt

path_root=$PWD

# patching
cp file.patch ./venv/lib/python3.6/site-packages/tornado
cd ./venv/lib/python3.6/site-packages/tornado
patch -p0 < file.patch

cd $path_root
sudo cp ./tornado_celery.conf /etc/supervisor/conf.d/

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
