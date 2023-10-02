#!/bin/bash
set -e  # Fail on first error

. .env/bin/activate
pip install -r requirements.txt

cd rankings
python manage.py migrate
python manage.py collectstatic
cd ..
