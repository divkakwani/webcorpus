#!/usr/bin/env bash

DATASTORE=${DATASTORE:-"$HOME/datastore"}

## Cleans things that could be broken
## See: https://github.com/scrapy/scrapy/issues/845#issuecomment-365488304
find $DATASTORE/jobs/current -name 'active.json' -type f -delete -print
find $DATASTORE/jobs/current -name 'p*' -type f -delete -print