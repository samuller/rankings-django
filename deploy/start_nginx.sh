#!/bin/bash
set -e  # Fail on first error

# ./prepare_repo.sh

# Copy current config
sudo cp nginx.conf /etc/nginx/sites-enabled/rankings.conf
sudo service nginx reload

./gunicorn.sh

