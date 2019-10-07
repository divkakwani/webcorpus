#!/usr/bin/env bash

DATASTORE=${DATASTORE:-"$HOME/datastore"}

if [[ ! -d "$DATASTORE/jobs" ]]
then
    mkdir "$DATASTORE/jobs"
fi

chkpt=0

while true
do
    SECONDS=0

    # run with a timeout of 6 hours
    corpora fetch-news --lang kn --srange 28,29 --timeout 21600
    wait $!

    duration=$SECONDS
    if (( duration > 120 ));
    then
        echo "Creating Checkpoint..."
        cp -r "$DATASTORE/jobs/current" "$DATASTORE/jobs/chkpt-$chkpt"
        chkpt=$((chkpt+1))
    fi
done
