#!/bin/bash
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
    cd rankings
    echo "flake8..."
    poetry run flake8 --exclude **/migrations/
    # We're not as strict about docstrings in our tests
    # poetry run flake8 --extend-ignore=D tests/
    echo "mypy..."
    poetry run mypy .
    # No "strict" type requirements for tests.
    # poetry run mypy tests/
    echo "black..."
    poetry run black --check .

    # cd svelte-ui && npm run lint && cd -
    # cd - && cd deploys && caddy fmt
}

format() {
    cd rankings && black . && cd -
    # cd svelte-ui && npm run format && cd -
    # cd deploys && caddy fmt --overwrite && cd -
}

test() {
    cd rankings
    # Run Django tests
    PYTHONWARNINGS=default poetry run coverage run --source='.' manage.py test --debug-mode .
    # Generate HTML coverage report
    poetry run coverage html --show-contexts
    # Print coverage report
    poetry run coverage report --fail-under=80
}

gen-docker() {
    # Official docker builds do templating with `gawk` script (and variables read from JSON with `jq` and
    # set with `eval`).
    # See: https://github.com/docker-library/python/blob/master/apply-templates.sh
    # And: https://github.com/docker-library/bashbrew/blob/master/scripts/jq-template.awk
    cd deploy
    # https://askubuntu.com/questions/1442884/replace-a-line-of-text-in-a-file-with-the-contents-of-another-file
    sed -e '/#:-- IMPORT: setup-app.Dockerfile --:#/{r setup-app.Dockerfile' -e 'd;}' Dockerfile.template > Dockerfile
    cd -
}

build() {
    # TODO: Cached builds:
    # - https://docs.gitlab.com/ee/ci/docker/docker_layer_caching.html
    # - https://stackoverflow.com/questions/52646303/is-it-possible-to-cache-multi-stage-docker-builds/68459169#68459169
    # - https://docs.docker.com/engine/reference/commandline/build/#cache-from
    VERSION=$(cat rankings/pyproject.toml | grep "^version = " | cut -d' ' -f3 | tr -d '"')
    gen-docker
    time docker build \
        --label "org.opencontainers.image.version=$VERSION" \
        --tag "rankings-site:0.0.1" \
        -f deploy/Dockerfile \
        .
}

if [ "$#" -gt 1 ]; then
    echo -n "Too many args. "
    help
fi

# Run function with same name of CLI argument (default to "help").
cmd=${1:-"help"}
$cmd
