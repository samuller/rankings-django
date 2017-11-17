## Installation

For development perform the following commands from the root directory.

Setup a virtualenv (optional, but recommended):

    virtualenv -p python3 .env

    . .env/bin/activate

Then install required modules:

    pip install -r requirements.txt

Setup the database:

    cd rankings
    python manage.py migrate

For admin access, create a user:

    python manage.py createsuperuser

And start a development server:

    python manage.py runserver


## Code structure

The `previous` app is the initial conversion of the old Flask application while using the same templates and database
with a minimum of changes. All other modules are part of the newer django rewrite which is still in progress.
