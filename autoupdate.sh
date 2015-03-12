#/bin/bash
echo "Starting deluged"
pkill deluged
deluged

echo "Starting deluge-web"
pkill deluge-web
deluge-web &

echo "Starting autoupdate myshow"
SLEEP="3600" # every hours

while true
do
  python3 myshow.py
  sleep ${SLEEP}
done

