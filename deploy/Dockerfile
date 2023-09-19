#
# Dockerfile for deploying the Ranking site's backend & frontend along with a
# Caddy routing server.
#
# Config format reference: https://docs.docker.com/engine/reference/builder/
#
# Build:
#     docker build -t rankings-site:0.0.1 -f deploy/Dockerfile .
# Run:
#     docker run -t --rm -p 8081:8080 rankings-site:0.0.1
# Debug in container:
#     docker run -it --rm rankings-site:0.0.1 bash
#
# Design:
# - Follow guidelines to make builds fast with layer caching:
#   - Layers: https://docs.docker.com/build/guide/layers/
#   - Cache: https://docs.docker.com/build/cache/
# - Use multi-stages for code re-use and smaller images: https://docs.docker.com/build/guide/multi-stage/
# - General best practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
# - TODO: Reproducible builds: https://medium.com/nttlabs/bit-for-bit-reproducible-builds-with-dockerfile-7cc2b9faed9f
#   - Especially when just changing app version and even on CI.
#
# Inspect each of the docker layers with dive tool:
# ```
# docker run --rm -it \
#     -v /var/run/docker.sock:/var/run/docker.sock \
#     wagoodman/dive:latest rankings-site:0.0.1
# ```
# - It's useful to set file tree (Tab) to filter out the unmodified (Ctrl+U),
#   sort by size (Ctrl+O) and also collapse all directories (Ctrl+Space).
# - Due to a bug with scrolling down in v0.11.0, you might also need to zoom
#   out to see all layers. See: https://github.com/wagoodman/dive/issues/469
#
# Intermediate stages can be built and run separately for debugging by
# using the "--target" flag with the stage's name:
# ```
# docker build --target backend-builder -t rankings-site-builder-test -f deploy/Dockerfile .
# docker run -it --rm rankings-site-builder-test bash
# ```
#
ARG OS_VERSION=bookworm
ARG NODE_VERSION=20.6.1
ARG PYTHON_VERSION=3.8.18
ARG POETRY_VERSION=1.4.2
ARG CADDY_VERSION=2.7.4
ARG GUNICORN_VERSION=21.2.0
# Paths to source code
ARG SRC_BE_DIR="./rankings/"
ARG SRC_UI_DIR="./svelte-ui/"
# Backend (BE) build paths
# We use same workdir as final so virtualenv is created with correct $PATH
ARG BE_WORKDIR="/app"
ARG BE_POETRY_VENV="/opt/poetry-venv"
ARG BE_POETRY_CACHE="/opt/.cache"
ARG BE_VENV="$BE_WORKDIR/.venv"
# User interface (UI) build paths
ARG UI_WORKDIR="/build-ui"
ARG UI_BUILD="$UI_WORKDIR/build"
# Paths for final "app" (release container)
ARG APP_BE_DIR="/app/backend"

# ---------------------------------------------------------------------------- #
########
# Install backend dependencies with Poetry. See:
# - https://stackoverflow.com/questions/72465421/how-to-use-poetry-with-docker
# - https://gist.github.com/soof-golan/6ebb97a792ccd87816c0bda1e6e8b8c2
# - https://github.com/orgs/python-poetry/discussions/1879
# - https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
########
FROM python:$PYTHON_VERSION-$OS_VERSION as backend-builder
ARG BE_WORKDIR
ARG SRC_BE_DIR
ARG POETRY_VERSION
ARG BE_POETRY_VENV
ARG BE_POETRY_CACHE
ARG GUNICORN_VERSION
# Configure Poetry
# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VENV=$BE_POETRY_VENV \
    # Tell Poetry where to place its cache and virtual environment
    POETRY_CACHE_DIR=$BE_POETRY_CACHE \
    # Tell poetry to create virtualenv as .venv directory in root of project
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

# Create a virtual environment just for poetry (to install poetry separated
# from system interpreter) and install it with pip
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add "poetry" to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR $BE_WORKDIR

# Copy only files that specify dependencies
COPY $SRC_BE_DIR/poetry.lock $SRC_BE_DIR/pyproject.toml ./

# Validate the project is properly configured
RUN poetry check

# Install dependencies
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root --without dev --no-cache --no-ansi

# Install gunicorn dependency
RUN poetry run pip install gunicorn==$GUNICORN_VERSION

# ---------------------------------------------------------------------------- #
# Stage to generate static website
FROM node:$NODE_VERSION as ui-builder
ARG UI_WORKDIR
ARG SRC_UI_DIR

WORKDIR $UI_WORKDIR

COPY $SRC_UI_DIR $UI_WORKDIR
# TODO: separate layer for dependencies
RUN npm ci

RUN npm run build

# ---------------------------------------------------------------------------- #
# The "combined-app" image combines all parts of the site into a single
# container image to simplify getting started easily. The services combined are:
# - Python Django backend, run via Gunicorn
# - Static SPA website built with Svelte
# - Caddy router
# We follow the one of the suggested recommendations of using supervisor to
# manage our multiple services within the Docker container.
# See: https://docs.docker.com/config/containers/multi-service_container/
FROM python:$PYTHON_VERSION-slim-$OS_VERSION as combined-app
ARG CADDY_VERSION
ARG UI_BUILD
ARG BE_VENV
ARG SRC_BE_DIR
ARG APP_BE_DIR
ARG POETRY_CACHE_DIR
# Set Python to output instantly to Docker logs (also helps prevents crashes losing logs)
ENV PYTHONUNBUFFERED=1

# Install generally required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Commands stripped in "slim" OS versions, but needed for further installs
    curl \
    gnupg \
    # Used as the root process manager
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Caddy
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    debian-keyring \
    debian-archive-keyring \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
       | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
       | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    caddy=${CADDY_VERSION} \
    && rm -rf /var/lib/apt/lists/*
# Install Caddy plugin for common logging format
RUN caddy add-package github.com/caddyserver/transform-encoder

# Copy the project venv folder from builder image 
COPY --from=backend-builder ${BE_VENV} /app/.venv
# Copy local files for application
COPY $SRC_BE_DIR $APP_BE_DIR

WORKDIR /app
# Installing our code as an (editable) package is currently only needed so that
# we can extract the version at runtime (without duplication) using the
# approach from: https://stackoverflow.com/questions/67085041/how-to-specify-version-in-only-one-place-when-using-pyproject-toml
RUN /app/.venv/bin/pip install -e $APP_BE_DIR

# Default supervisor config: /etc/supervisor/conf.d/supervisord.conf
COPY deploy/supervisord.conf /app
COPY deploy/Caddyfile /app
# Copy the statically built UI files
COPY --from=ui-builder ${UI_BUILD} /var/www/html

# Default vars for supervisor
ENV GUNICORN_WORKERS=5
ENV GUNICORN_TIMEOUT=30
# Run application
EXPOSE 8080
# Set default directory when app starts (or container is entered)
WORKDIR /app
# Default command to run if nothing else is specified.
CMD ["/usr/bin/supervisord","-c","/app/supervisord.conf"]
