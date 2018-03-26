#!/usr/bin/env bash
. ./fill.sh

echo [supervisord]
echo environment=PORT=$PORT,NAME=$NAME,USER=$USER,PASSWORD=$PASSWORD,HOST=$HOST,PORTDB=$PORTDB
echo
echo [program:tornado]
echo environment=PATH=$PATH_BY_PROJ/venv/bin
echo command=$PATH_BY_PROJ/rpc_server.py
echo directory=$PATH_BY_PROJ
echo user=$USERSYS
echo numprocs=1
echo stdout_logfile=$PATH_BY_PROJ/logs/tornado.log
echo stderr_logfile=$PATH_BY_PROJ/logs/tornado.log
echo autostart=true
echo autorestart=true
echo startsecs=10
echo priority=997
echo
echo
echo [program:tornado_celery]
echo command=$PATH_BY_PROJ/venv/bin/celery --app=messaging.app:APP worker --loglevel=INFO -E
echo directory=$PATH_BY_PROJ
echo user=$USERSYS
echo numprocs=1
echo stdout_logfile=$PATH_BY_PROJ/logs/celery-worker.log
echo stderr_logfile=$PATH_BY_PROJ/logs/celery-worker.log
echo autostart=true
echo autorestart=true
echo startsecs=10
echo stopwaitsecs = 600
echo killasgroup=true
echo priority=998
echo
echo
echo [program:flower]
echo environment=PATH=$PATH_BY_PROJ/venv/bin
echo command=/bin/bash -c \"celery flower\"
echo directory=$PATH_BY_PROJ
echo user=$USERSYS
echo numprocs=1
echo stdout_logfile=$PATH_BY_PROJ/logs/flower.log
echo stderr_logfile=$PATH_BY_PROJ/logs/flower.log
echo autostart=true
echo autorestart=true
echo startsecs=10
echo priority=999
