## Installation

For development perform the following commands from the root directory.

Setup a virtualenv (optional, but recommended):

    virtualenv -p python3 .env

    . .env/bin/activate

Then install required modules:

    pip install -r requirements.txt

Setup the database:

    python manage.py migrate

And start a development server:

    python manage.py runserver

For admin access, create a user:

    python manage.py createsuperuser

