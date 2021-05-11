FROM python:3

COPY requirements.txt .
COPY requirements_dev.txt .
COPY requirements.lock .

RUN \
  apt-get update && \
  apt-get install -y spatialite-bin libsqlite3-mod-spatialite \
     binutils libproj-dev gdal-bin && \
  pip install -U pip && pip install pipenv && \
  pip install -r requirements_dev.txt && \
  rm -rf /var/lib/apt/lists/*

EXPOSE 8000