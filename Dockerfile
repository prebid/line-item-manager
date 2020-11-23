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
    gcc \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    make \
    musl-dev \
    openssl-dev \
    tini

WORKDIR ${APP_DIR}

# File upload
COPY setup.py ${APP_DIR}/
COPY setup.cfg ${APP_DIR}/
COPY MANIFEST.in ${APP_DIR}/

RUN pip install --upgrade pip
RUN pip3 install -e .[test]

COPY line_item_manager/ ${APP_DIR}/line_item_manager
COPY tests/ ${APP_DIR}/tests/
COPY Makefile ${APP_DIR}/
COPY tox.ini requirements_dev.txt ${APP_DIR}/
RUN chown -R ${USER}: ${APP_DIR}

USER ${USER}

ENTRYPOINT ["tini", "--"]
