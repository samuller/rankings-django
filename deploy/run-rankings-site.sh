#!/usr/bin/env bash
#
# Run script like this:
#     tmux
#     sudo -u rankings /home/rankings/run-rankings-site.sh
#

# Exit on first error
set -e
# Print out commands being run
set -x

# These commands needs to be run as user that has poetry installed locally (e.g. su rankings)
# source ~/.profile
. ~/.profile
poetry --version

cd ~/rankings-django
cd rankings
poetry run gunicorn rankings.wsgi:application \
    --timeout 10000 \
    --workers 3 \
    --log-file ~/logs/gunicorn.log \
    --capture-output
