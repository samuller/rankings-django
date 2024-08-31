#
# VSCode devcontainer for development with: Ubuntu + Node + Python + Poetry
#
ARG UBUNTU_VERSION=24.04
# Match with NODE_VERSION in built docker
ARG NODE_MAJOR_VERSION=22
ARG PYTHON_VERSION=3.8
ARG POETRY_VERSION=1.4.2

FROM ubuntu:$UBUNTU_VERSION
# FROM creates a new build stage, so we need to redeclare any arguments we want to keep.
# See: https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG NODE_MAJOR_VERSION
ARG PYTHON_VERSION
ARG POETRY_VERSION

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN unset DISPLAY
ENV DEBIAN_FRONTEND=noninteractive

# Switch to automatic mirror select mode if apt downloads are slow.
# RUN sed -i 's http://archive.ubuntu.com/ubuntu/ mirror://mirrors.ubuntu.com/mirrors.txt ' /etc/apt/sources.list

########
# Install Node
########
RUN apt-get update \
    && apt-get -y install \
        ca-certificates \
        curl \
        gnupg \
        sudo

# 30s
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
    | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR_VERSION.x nodistro main" \
    | sudo tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs

########
# Install Python
########

RUN echo python${PYTHON_VERSION}

# Install build dependencies.
# This will bloat the image, but is necessary to "poetry install" the dependencies
# then install specific Python version.
# 288s
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa && apt-get install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev
RUN python${PYTHON_VERSION} -m venv /opt/venv
# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

########
# Install Pip
########

# Install latest pip
RUN /opt/venv/bin/python${PYTHON_VERSION} -m pip install --upgrade pip

# Note that we don't clear out the APT-GET cache -- one often needs to install
# packages inside the devcontainer.
RUN apt-get update && apt-get -qqy install apt-transport-https iputils-ping sudo gnupg2 tzdata

########
# Setup vscode user
########

# Set whole sudo group to not need to supply password when sudoing.
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Use non-root user for dev.
# Since Ubuntu 24.04 the docker has included this user.
# See: https://askubuntu.com/questions/1513927/ubuntu-24-04-docker-images-now-includes-user-ubuntu-with-uid-gid-1000
USER ubuntu

########
# Install Poetry
########
# 60s
RUN curl -sSL https://install.python-poetry.org | python${PYTHON_VERSION} -

########
# Setups for specific dependencies
########

# Needed for cv2.
# 270s
# RUN sudo apt-get install -y ffmpeg libsm6 libxext6

ENV DJANGO_DEBUG="True"

# Default command to run if nothing else is specified.
CMD ["/bin/bash"]
