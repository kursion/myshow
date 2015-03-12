#/usr/bin/bash

SLEEP="3600" # every hours

while true
do
  python3 myshow.py
  sleep ${SLEEP}
done
