#!/bin/bash
#
# Script for running commonly used commands quickly, e.g. "./run.sh lint". See: "./run.sh help".
#

# Fail on first error.
set -e

man_help="List all commands available."
help() {
    echo "You have to provide a command to run, e.g. '$0 lint'"
    # List declared functions that are not from exports (-fx).
    commands=$(echo "$KNOWN_COMMANDS" | cut -d' ' -f 3 | tr '\n' ' ')
    echo "All commands available are:"
    echo
    (
        for cmd in ${commands}; do
            doc_name=man_$(echo "$cmd" | tr - _)
            echo -e "  $cmd\t\t\t${!doc_name}"
        done
    ) | column -t -s$'\t'
    echo
    exit
}

man_lint="Run lint, formatting and type checks for Python code."
lint() {
    if [ "$#" -gt 0 ]; then
        echo "Too many args."
        exit
    fi

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

man_format="Auto-format all Python code."
format() {
    if [ "$#" -gt 0 ]; then
        echo "Too many args."
        exit
    fi

    cd rankings && black . && cd -
    # cd svelte-ui && npm run format && cd -
    # cd deploys && caddy fmt --overwrite && cd -
}

man_test="Run tests for Python code."
test() {
    if [ "$#" -gt 0 ]; then
        echo "Too many args."
        exit
    fi
    cd rankings
    # Run Django tests
    PYTHONWARNINGS=default poetry run coverage run --source='.' manage.py test --debug-mode .
    # Generate HTML coverage report
    poetry run coverage html --show-contexts
    # Print coverage report
    poetry run coverage report --fail-under=80
}

man_gen_docker="Prepare files for building docker images."
gen-docker() {
    if [ "$#" -gt 0 ]; then
        echo "Too many args."
        exit
    fi
    # Create stripped-down version of pyproject.toml (no version and comments) for use with Dockerfile so
    # meaningless changes to it won't invalidate the following caching layers.
    cat rankings/pyproject.toml \
        | sed 's/^version = ".*"/version = "0"/' \
        | sed 's/^\s*#.*//' \
        | sed '/^$/d' \
        > rankings/pyproject.nover.toml

    # Official docker builds do templating with `gawk` script (and variables read from JSON with `jq` and
    # set with `eval`).
    # See: https://github.com/docker-library/python/blob/master/apply-templates.sh
    # And: https://github.com/docker-library/bashbrew/blob/master/scripts/jq-template.awk
    cd deploy
    # https://askubuntu.com/questions/1442884/replace-a-line-of-text-in-a-file-with-the-contents-of-another-file
    sed -e '/#:-- IMPORT: setup-app.Dockerfile --:#/{r setup-app.Dockerfile' -e 'd;}' Dockerfile.template > Dockerfile
    cd -
}

man_build="Build docker image."
build() {
    if [ "$#" -gt 1 ]; then
        echo "Too many args."
        exit
    fi

    # TODO: Cached builds:
    # - https://docs.gitlab.com/ee/ci/docker/docker_layer_caching.html
    # - https://stackoverflow.com/questions/52646303/is-it-possible-to-cache-multi-stage-docker-builds/68459169#68459169
    # - https://docs.docker.com/engine/reference/commandline/build/#cache-from
    IMAGE="rankings-site-test"
    API_VERSION=$(cat rankings/pyproject.toml | grep "^version = " | cut -d' ' -f3 | tr -d '"')
    UI_VERSION=$(cat svelte-ui/package.json | grep '"version": "' | cut -d':' -f2 | tr -d ' ",')
    GIT_HASH=$(git rev-parse HEAD)
    gen-docker
    time docker build \
        --label "org.opencontainers.image.version=$UI_VERSION" \
        --label "org.opencontainers.image.revision=$GIT_HASH" \
        --tag "$IMAGE:$UI_VERSION" \
        --tag "$IMAGE:latest" \
        -f deploy/Dockerfile \
        .
}

# Find all declared functions that are not from exports (-fx). This will only pick up functions before this point.
KNOWN_COMMANDS=$(declare -F | grep -v "\-fx")

# Run function with same name of CLI argument (default to "help").
cmd=${1:-"help"}
# Remove argument we've already used.
shift
$cmd "$@"
