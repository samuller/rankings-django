#
# Script for running commonly used commands quickly, e.g. "./run.sh lint". See: "./run.sh help".
#

# Fail on first error.
set -e

help() {
    echo "You have to provide a command to run, e.g. '$0 lint'"
    # Get all function names and then add indent to each line.
    commands=$(compgen -A function | sed 's/^/  /')
    echo -e "All commands available are:\n$commands"
    exit
}

lint() {
    echo "flake8..."
    poetry run flake8 --exclude **/*/migrations/
    # We're not as strict about docstrings in our tests
    # poetry run flake8 --extend-ignore=D tests/
    echo "mypy..."
    poetry run mypy .
    # No "strict" type requirements for tests.
    # poetry run mypy tests/
    echo "black..."
    poetry run black --check rankings/
}

format() {
    black rankings/
}

test() {
    # Run Django tests
    poetry run coverage run --source='.' rankings/manage.py test --debug-mode rankings/
    # Generate HTML coverage report
    poetry run coverage html --show-contexts
    # Print coverage report
    poetry run coverage report --fail-under=75
}

if [ "$#" -gt 1 ]; then
    echo -n "Too many args. "
    help
fi

# Run function with same name of CLI argument (default to "help").
cmd=${1:-"help"}
$cmd
