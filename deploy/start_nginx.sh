#!/bin/bash
set -e  # Fail on first error

. .env/bin/activate
cd rankings
python manage.py collectstatic
cd ..

# Copy current config
sudo cp nginx.conf /etc/nginx/sites-enabled/rankings.conf
sudo service nginx reload

./gunicorn.sh

