#!/usr/bin/env bash
#
# Wrapper script to run management commands within the development Docker image. Arguments to the
# script are passed to ./manage.py.

# Change to this script's directory
cd "$( dirname "${BASH_SOURCE[0]}")"

# Run manage.py
set -x
exec ./compose.sh development run --rm development_app ./manage.py $@
