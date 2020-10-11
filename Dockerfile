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

# App dependencies
COPY setup.py ${APP_DIR}/
RUN pip3 install -e .

# File upload
COPY line_item_manager/ ${APP_DIR}/line_item_manager
COPY tests/ ${APP_DIR}/tests/

USER ${USER}

ENTRYPOINT ["tini", "--"]
