#
# Dockerfile for deploying the Ranking site's backend & frontend with Caddy routing server.
#
# ```
# docker build -t rankings-site:0.0.1 -f deploy/Dockerfile .
# docker run -it --rm rankings-site:0.0.1 bash
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
ARG UBUNTU_VERSION=22.04
ARG NODE_MAJOR_VERSION=20
ARG PYTHON_VERSION=3.8.18
ARG POETRY_VERSION=1.4.2
ARG CADDY_VERSION=2.7.4
# Paths to source code
ARG SRC_BE_DIR="./rankings/"
ARG SRC_UI_DIR="./svelte-ui/"
# Backend (BE) build paths
ARG BE_WORKDIR="/build-be"
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
# Build backend with Python + Poetry.
# See: https://stackoverflow.com/questions/72465421/how-to-use-poetry-with-docker
# And: https://gist.github.com/soof-golan/6ebb97a792ccd87816c0bda1e6e8b8c2
########
FROM python:$PYTHON_VERSION as backend-builder
ARG BE_WORKDIR
ARG SRC_BE_DIR
ARG POETRY_VERSION
ARG BE_POETRY_VENV
ARG BE_POETRY_CACHE
# Configure Poetry
# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_HOME="/opt/poetry"
ENV BE_POETRY_VENV=$BE_POETRY_VENV
# Tell Poetry where to place its cache and virtual environment
ENV BE_POETRY_CACHE=$BE_POETRY_CACHE
# Tell poetry to create virtualenv as .venv directory in root of project
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_NO_INTERACTION=1

# Create a virtual environment just for poetry (to install poetry separated
# from system interpreter) and install it with pip
RUN python3 -m venv $BE_POETRY_VENV \
    && $BE_POETRY_VENV/bin/pip install -U pip setuptools \
    && $BE_POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add "poetry" to PATH
ENV PATH="${PATH}:${BE_POETRY_VENV}/bin"

WORKDIR $BE_WORKDIR

# Copy only files that specify dependencies
COPY $SRC_BE_DIR/poetry.lock $SRC_BE_DIR/pyproject.toml ./

# [OPTIONAL] Validate the project is properly configured
RUN poetry check

# Install dependencies
RUN poetry install --no-cache --no-ansi --no-root --without dev

# ---------------------------------------------------------------------------- #
# Finally create a new stage for running the app
FROM python:$PYTHON_VERSION as app
ARG CADDY_VERSION
ARG UI_BUILD
ARG BE_VENV
ARG SRC_BE_DIR
ARG APP_BE_DIR



WORKDIR /app
# Copy the project venv folder from builder image 
COPY --from=backend-builder ${BE_VENV} ./.venv
# Copy local files for application
COPY $SRC_BE_DIR $APP_BE_DIR
COPY deploy/Caddyfile /app

# Run application
EXPOSE 5000
# Default command to run if nothing else is specified.
CMD ["/bin/bash"]
