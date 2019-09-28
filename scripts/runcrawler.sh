#!/usr/bin/env bash

if [[ ! -d "data/job" ]]
then
    mkdir data/job
fi

chkpt=0

while true
do
    # run with a timeout of 6 hours - 21600
    python3 main.py fetch-news --lang kn --srange 16,17 --timeout 10
    cp -r data/job "data/chkpt-$chkpt"
    chkpt=$((chkpt+1))
done
