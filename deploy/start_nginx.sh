. .env/bin/activate
cd rankings
python manage.py collectstatic
cd ..

sudo cp nginx.conf /etc/nginx/sites-enabled/
sudo service nginx reload

./gunicorn.sh

