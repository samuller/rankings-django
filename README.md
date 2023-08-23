
[![Build Status](https://github.com/samuller/rankings-django/workflows/tests/badge.svg)](https://github.com/samuller/rankings-django/actions)

## Development

For development perform the following commands from the root directory.

### Setup virtualenv

[Install poetry](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions):
```shell
curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.4.2 python -
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
```console
cd rankings
python manage.py migrate
```

For admin access, create a user:
```console
python manage.py createsuperuser
```

And start a development server:
```console
python manage.py runserver
```

You can also add test data:
```console
python manage.py loaddata game.json
python manage.py loaddata players.json
```

## Code structure

The `previous` app is the initial conversion of the old Flask application while using the same templates and database
with a minimum of changes. All other modules are part of the newer django rewrite which is still in progress.
