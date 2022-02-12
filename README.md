
## Development

### Installation

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

You can also add test data:

    python manage.py loaddata game.json
    python manage.py loaddata players.json


### In Devcontainer

In case you don't want the thousands of library files to be installed on your local system, you can install them in the Devcontainer docker image with the following:

```console
sudo mkdir /workspace/.env
virtualenv -p python3 /workspace/.env
. /workspace/.env/bin/activate
pip install -r requirements.txt
```


## Code structure

The `previous` app is the initial conversion of the old Flask application while using the same templates and database
with a minimum of changes. All other modules are part of the newer django rewrite which is still in progress.
