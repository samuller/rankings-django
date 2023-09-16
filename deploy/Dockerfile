#
# Dockerfile for deploying the Ranking site's backend & frontend with Caddy routing server.
#
# ```
# docker build -t ranking-site:0.0.1 -f deploy/Dockerfile .
# docker run -it --rm ranking-site:0.0.1 bash
# ```
#
# Inspect each of the docker layers with dive tool:
# ```
# docker run --rm -it \
#     -v /var/run/docker.sock:/var/run/docker.sock \
#     wagoodman/dive:latest ranking-site:0.0.1
# ```
# - It's useful to set file tree (Tab) to filter out the unmodified (Ctrl+U),
#   sort by size (Ctrl+O) and also collapse all directories (Ctrl+Space).
# - Due to a bug with scrolling down in v0.11.0, you might also need to zoom
#   out to see all layers. See: https://github.com/wagoodman/dive/issues/469
#
# Intermediate stages can be built and run separately for debugging by
# using the "--target" flag with the stage's name:
# ```
# docker build --target backend-builder -t ranking-site-builder-test -f deploy/Dockerfile .
# docker run -it --rm ranking-site-builder-test bash
# ```
#
ARG UBUNTU_VERSION=22.04
ARG NODE_MAJOR_VERSION=20
ARG PYTHON_VERSION=3.8.18
ARG POETRY_VERSION=1.4.2

ARG BACKEND_DIR="./rankings/"
ARG UI_DIR="./svelte-ui/"

ARG POETRY_VENV="/opt/poetry-venv"
ARG POETRY_CACHE_DIR="/opt/.cache"
ARG APP_VENV="/app/.venv"

# ---------------------------------------------------------------------------- #
########
# Build backend with Python + Poetry.
# See: https://stackoverflow.com/questions/72465421/how-to-use-poetry-with-docker
# And: https://gist.github.com/soof-golan/6ebb97a792ccd87816c0bda1e6e8b8c2
########
FROM python:$PYTHON_VERSION as backend-builder
ARG BACKEND_DIR
ARG POETRY_VERSION
ARG POETRY_VENV
ARG POETRY_CACHE_DIR
# Configure Poetry
# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VENV=$POETRY_VENV
# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=$POETRY_CACHE_DIR
# Tell poetry to create virtualenv as .venv directory in root of project
ENV POETRY_VIRTUALENVS_IN_PROJECT=1
ENV POETRY_NO_INTERACTION=1

# Create a virtual environment just for poetry (to install poetry separated
# from system interpreter) and install it with pip
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add "poetry" to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Copy only files that specify dependencies
COPY $BACKEND_DIR/poetry.lock $BACKEND_DIR/pyproject.toml ./

# [OPTIONAL] Validate the project is properly configured
RUN poetry check

# Install dependencies
RUN poetry install --no-cache --no-ansi --no-root --without dev

# ---------------------------------------------------------------------------- #
# Finally create a new stage for running the app
FROM python:$PYTHON_VERSION
ARG BACKEND_DIR
ARG APP_VENV

WORKDIR /app

# Copy the project venv folder from builder image 
COPY --from=backend-builder ${APP_VENV} ./.venv

# Copy local files for application
COPY $BACKEND_DIR /app

# Run application
EXPOSE 5000
# Default command to run if nothing else is specified.
CMD ["/bin/bash"]
