#!/bin/bash
wait_time=1
while true
do
    start_ts=$(date +%s)
    python -u bot.py >> dankpy.log 2>&1

    dead_ts=$(date +%s)
    if [[ $((dead_ts-start_ts)) -ge 30 ]]; then
        wait_time=1
    else
        wait_time=$(($wait_time * 2))
        wait_time=$(($wait_time > 30 ? 30 : $wait_time))
    fi
    echo dead at $dead_ts > danksh.log 2>&1
    sleep $wait_time
done