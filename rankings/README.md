## Development

For development perform the following commands from the root directory.

### Setup virtualenv

[Install poetry](https://python-poetry.org/docs/#installing-with-the-official-installer):
```shell
curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.8.3 python -
```

Install packages:
```shell
poetry install
```

Activate virtual environment:
```shell
poetry shell
```

### Installation

Setup the database:
```shell
cd rankings
python manage.py migrate
```

For admin access, create a user:
```shell
python manage.py createsuperuser
```

And start a development server:
```shell
python manage.py runserver
```

You can also add test data:
```shell
python manage.py loaddata game.json
python manage.py loaddata players.json
```

## Code structure

The `previous` app is the initial conversion of the old Flask application while using the same templates and database
with a minimum of changes. All other modules are part of the newer django rewrite which is still in progress.
