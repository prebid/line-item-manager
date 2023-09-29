FROM python:3.11-slim

ENV USER=app \
    APP_DIR=/home/app \
    PIP_NO_CACHE_DIR=0

RUN useradd -ms /bin/bash ${USER}

# System dependencies
RUN apt-get -y update
RUN apt-get install -y --no-install-recommends \
  build-essential \
  libffi-dev \
  libpq-dev \
  tini

WORKDIR ${APP_DIR}

# Update pip
RUN pip3 install --upgrade pip setuptools
RUN pip3 install wheel

# App dependencies
COPY setup.py ${APP_DIR}/
COPY setup.cfg ${APP_DIR}/
COPY MANIFEST.in ${APP_DIR}/

RUN pip install --upgrade pip
RUN pip3 install -e .[release,test]

COPY line_item_manager/ ${APP_DIR}/line_item_manager
COPY tests/ ${APP_DIR}/tests/
COPY Makefile ${APP_DIR}/
COPY *.rst ${APP_DIR}/

RUN chown -R ${USER}: ${APP_DIR}
USER ${USER}

ENTRYPOINT ["tini", "--"]
