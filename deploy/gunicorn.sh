#!/bin/bash
set -e  # Fail on first error

. .env/bin/activate
cd rankings
# http://docs.gunicorn.org/en/stable/settings.html
gunicorn rankings.wsgi:application --timeout 300 --workers 3 --log-file ~/logs/gunicorn.log --capture-output