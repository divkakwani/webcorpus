#!/usr/bin/env bash

if [[ ! -d "data/job" ]]
then
    mkdir data/job
fi

chkpt=0

while true
do
    SECONDS=0

    # run with a timeout of 6 hours
    python3 main.py fetch-news --lang kn --srange 8,20 --timeout 21600
    wait $!

    duration=$SECONDS
    if (( duration > 60 ));
    then
        echo "Creating Checkpoint..."
        cp -r data/job "data/chkpt-$chkpt"
        chkpt=$((chkpt+1))
    fi
done
