#!/bin/bash
LOGFILE=/home/ubuntu/webapps/logs/guni.log
GUNI_PID=/home/ubuntu/webapps/djecommerce/djecommerce/deploy/guni.pid
NUM_WORKERS=3
cd /home/ubuntu/webapps/djecommerce/djecommerce
source /home/ubuntu/.virtualenvs/dj1.9/bin/activate
exec gunicorn -D --pid $GUNI_PID -w $NUM_WORKERS --log-file=$LOGFILE djecommerce.wsgi:application
