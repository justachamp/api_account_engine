#!/bin/bash 
set -e

_wait(){
	/bin/bash ./wait-for-it.sh ${RDS_HOSTNAME}:${RDS_PORT} -s -t 30 -- "$@"
}

if [ "$1" == "bootstrap" ]; then
    _wait python manage.py migrate && \
    python manage.py loaddata initial_data.json
elif [ "$1" == "sudo" ]; then
	_wait python manage.py sudo
else
	_wait echo "DB Ready"
	exec "$@"
fi
