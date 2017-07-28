#!/bin/bash
set -e  # Fail on first error

cd rankings
gunicorn rankings.wsgi:application --timeout 300 --workers 3
