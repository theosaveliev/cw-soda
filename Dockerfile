# syntax=docker/dockerfile:1
FROM ubuntu:noble

RUN yes | unminimize
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends less vim nano git curl ca-certificates rhash xxd mc locales man-db \
    && rm -Rf /var/lib/apt/lists/* \
    && locale-gen "en_US.UTF-8"

USER ubuntu:ubuntu
WORKDIR /home/ubuntu
ENV LANG="en_US.UTF-8"

ADD --chown=ubuntu:ubuntu https://astral.sh/uv/install.sh uv-installer.sh
RUN sh uv-installer.sh && rm uv-installer.sh
ENV PATH="/home/ubuntu/.local/bin/:$PATH"

RUN git clone --depth 1 --branch v0.4.1 https://github.com/theosaveliev/cw-soda.git cw-soda \
    && uv tool install --no-cache --directory cw-soda . \
    && rm -Rf cw-soda
