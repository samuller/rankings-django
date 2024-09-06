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

    # Change into Python directory so Poetry can use pyproject.toml
    cd rankings
    echo "ruff check..."
    # Run ruff from parent directory so that it can will find and use .gitignore
    poetry run ruff check ..
    # We're not as strict about docstrings in our tests
    # poetry run flake8 --extend-ignore=D tests/
    echo "ruff format..."
    poetry run ruff format --check ..
    echo "mypy..."
    poetry run mypy .
    # Start doing strict checks on some code.
    poetry run mypy --strict --allow-subclassing-any --allow-untyped-defs previous/{models,utils}.py
    # No "strict" type requirements for tests.
    # poetry run mypy tests/

    # cd svelte-ui && npm run lint && cd -
    # cd - && cd deploys && caddy fmt
}

man_format="Auto-format all Python code."
format() {
    if [ "$#" -gt 0 ]; then
        echo "Too many args."
        exit
    fi

    cd rankings && ruff format .. && cd -
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
    PYTHONWARNINGS=always poetry run coverage run --source='.' manage.py test --debug-mode .
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
    # Create stripped-down version of pyproject.toml for use with Dockerfile so meaningless changes to it
    # won't invalidate the following caching layers. We remove the project version, any comments and also
    # the "readme" config since that breaks the "poetry check" command we perform on the file when we only
    # use it to install dependencies.
    cat rankings/pyproject.toml \
        | sed 's/^version = ".*"/version = "0"/' \
        | sed 's/^\s*#.*//' \
        | sed 's/^readme = ".*"//' \
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

    API_VERSION=$(cat rankings/pyproject.toml | grep "^version = " | cut -d' ' -f3 | tr -d '"')
    UI_VERSION=$(cat svelte-ui/package.json | grep '"version": "' | cut -d':' -f2 | tr -d ' ",')
    GIT_HASH=$(git rev-parse HEAD)
    case "$1" in
        prod)
            IMAGE="samuller/rankings-site"
            TARGET="combined-app-alpine"
            IMAGE_VERSION="$API_VERSION-$UI_VERSION"
            ;;
        test)
            IMAGE="samuller/rankings-site-test"
            TARGET="test-app"
            IMAGE_VERSION="$API_VERSION-$UI_VERSION"
            ;;
        *)
            echo "Invalid arg '$1' expected 'prod' or 'test'."
            exit
            ;;
    esac

    echo "Building $IMAGE:$IMAGE_VERSION..."
    # TODO: Cached builds:
    # - https://docs.gitlab.com/ee/ci/docker/docker_layer_caching.html
    # - https://stackoverflow.com/questions/52646303/is-it-possible-to-cache-multi-stage-docker-builds/68459169#68459169
    # - https://docs.docker.com/engine/reference/commandline/build/#cache-from
    gen-docker
    # "--no-cache" is only needed when we want to update build date in UI's __APP_VERSION__.
    time docker build \
        --label "org.opencontainers.image.created=$(date -Is)" \
        --label "org.opencontainers.image.version=$IMAGE_VERSION" \
        --label "org.opencontainers.image.revision=$GIT_HASH" \
        --target "$TARGET" \
        --tag "$IMAGE:$IMAGE_VERSION" \
        --tag "$IMAGE:latest" \
        -f deploy/Dockerfile \
        .
}

# Find all declared functions that are not from exports (-fx). This will only pick up functions before this point.
KNOWN_COMMANDS=$(declare -F | grep -v "\-fx")

# If column command is not available, create a no-op function to replace it and prevent errors.
# Alternatively, install it with: apt-get install -y bsdmainutils
if ! type column >/dev/null 2>&1
then function column { cat - ;}
fi

# Run function with same name of CLI argument (default to "help").
cmd=${1:-"help"}
if [ "$#" -gt 0 ]; then
    # Remove argument we've already used.
    shift
fi
$cmd "$@"
