#!/usr/bin/env sh

sh -c "/usr/bin/supervisord -n -c /etc/supervisord.conf &&
supervisorctl reread &&
supervisorctl update &&
supervisorctl start all"
