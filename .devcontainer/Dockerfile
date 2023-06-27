#
# VSCode devcontainer for development with: Ubuntu + Python + Poetry
#
ARG UBUNTU_VERSION=22.04

FROM ubuntu:$UBUNTU_VERSION

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN unset DISPLAY
ENV DEBIAN_FRONTEND=noninteractive

########
# Install node
########
RUN apt-get update && apt-get -y install software-properties-common build-essential curl wget unzip sudo

RUN curl -sSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && \
    apt-get install -y nodejs

########
# Setup vscode user
########

# create the non-root user that we're going to use for dev
# -m: create home
# -s: set shell
# -G sudo: add to sudo group
RUN useradd -ms /bin/bash -G sudo vscode
# the whole sudo group does not need to supply password when sudoing
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# pre-create the pypoetry cache directory by the non-root user
# so that the named-volume we mount there will be writable to vscode
USER vscode
# in-case base image sets this to root, we have to reset to vscode's home (USER
# statement not sufficient)
ENV HOME=/home/vscode

# default command to run if nothing else is specified
CMD ["/bin/bash"]
