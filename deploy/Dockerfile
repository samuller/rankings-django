#
# Dockerfile for deploying the Ranking site's backend & frontend with Caddy routing server.
#
# ```
# docker build -t rankings-site:0.0.1 -f deploy/Dockerfile .
# docker run -it --rm rankings-site:0.0.1 bash
# docker run -t --rm -p 8081:8080 rankings-site:0.0.1
# ```
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
FROM node:$NODE_VERSION as ui-builder
ARG UI_WORKDIR
ARG SRC_UI_DIR

WORKDIR $UI_WORKDIR

COPY $SRC_UI_DIR $UI_WORKDIR

RUN npm ci

RUN npm run build

# ---------------------------------------------------------------------------- #
# Finally create a new stage for running the app
FROM python:$PYTHON_VERSION-slim-$OS_VERSION as combined-app
ARG CADDY_VERSION
ARG UI_BUILD
ARG BE_VENV
ARG SRC_BE_DIR
ARG APP_BE_DIR
ARG POETRY_CACHE_DIR
# Set Python to output instantly to Docker logs (also helps prevents crashes losing logs).
ENV PYTHONUNBUFFERED=1

# Install needed files that are stripped in "slim" OS versions
RUN apt-get update \
    && apt-get install -y --no-install-recommends gnupg curl

# Install Caddy
RUN apt-get update \
    && apt-get install -y --no-install-recommends debian-keyring \
        debian-archive-keyring apt-transport-https \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
       | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
       | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update \
    && apt-get install -y caddy=${CADDY_VERSION}
# Install Caddy plugin for common logging format
RUN caddy add-package github.com/caddyserver/transform-encoder

RUN apt-get update && apt-get install -y supervisor

# Copy the project venv folder from builder image 
COPY --from=backend-builder ${BE_VENV} /app/.venv
# Copy local files for application
COPY $SRC_BE_DIR $APP_BE_DIR

WORKDIR /app
RUN /app/.venv/bin/pip install -e $APP_BE_DIR

# Default supervisor config: /etc/supervisor/conf.d/supervisord.conf
COPY deploy/supervisord.conf /app
COPY deploy/Caddyfile /app
# Copy the statically built UI files
COPY --from=ui-builder ${UI_BUILD} /var/www/html

# Run application
EXPOSE 8080
# Default command to run if nothing else is specified.
WORKDIR /app
CMD ["/usr/bin/supervisord","-c","/app/supervisord.conf"]
