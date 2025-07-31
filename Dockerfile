# syntax=docker/dockerfile:1
FROM ubuntu:noble

RUN yes | unminimize
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends ca-certificates locales curl less vim nano xxd exiftool keepassxc \
    && rm -Rf /var/lib/apt/lists/* \
    && locale-gen "en_US.UTF-8"

USER ubuntu:ubuntu
WORKDIR /home/ubuntu
ENV LANG="en_US.UTF-8"

ADD --chown=ubuntu:ubuntu https://astral.sh/uv/install.sh uv-installer.sh
RUN sh uv-installer.sh && rm uv-installer.sh
ENV PATH="/home/ubuntu/.local/bin/:$PATH"

ADD --chown=ubuntu:ubuntu . cw-soda
RUN uv tool install --no-cache --directory cw-soda . \
    && rm -Rf cw-soda \
    && uv tool install "steganon[cli]"