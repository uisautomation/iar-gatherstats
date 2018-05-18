#!/usr/bin/env bash
#
# Run a database migration and start the development server.
set -xe

cd /usr/src/app

python ./manage.py migrate

exec python ./manage.py gatherstats
