#!/bin/bash
shutdown()
{
  kill -TERM "$child" 2>/dev/null
  exit 0
}

trap shutdown SIGTERM
trap shutdown SIGINT

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

for (( ; ; )) do
    sleep 60 & wait
    python3 bot.py &
    child=$!
    wait "$child"
done
