ARG ALPINE_VERSION=3.11

FROM python:3.8-alpine${ALPINE_VERSION}
ARG ALPINE_VERSION

ENV USER=app \
    APP_DIR=/home/app \
    PIP_NO_CACHE_DIR=0

RUN addgroup -S ${USER} && \
    adduser -S ${USER} -G ${USER}

RUN apk add --no-cache \
    bash \
    curl \
    tini

WORKDIR ${APP_DIR}

# File upload
COPY setup.py ${APP_DIR}/
COPY MANIFEST.in ${APP_DIR}/
COPY line_item_manager/ ${APP_DIR}/line_item_manager
COPY tests/ ${APP_DIR}/tests/

RUN pip3 install -e .

USER ${USER}

ENTRYPOINT ["tini", "--"]
