# Production image for docker-compose deployment.
# Build context is the repo root: `docker build -f deploy/Dockerfile ..`
# This file is additive — it does not modify any upstream file. It diverges
# from Dockerfile.fly in three ways:
#   1. Multi-stage: node tooling never lands in the runtime image.
#   2. Installs requirements.txt instead of requirements_dev.txt (no pytest/tox/mypy in runtime).
#   3. Adds an HTTP HEALTHCHECK so docker compose can report container health.

###############################################################################
# Stage 1 — frontend assets
# Build Tailwind + webpack output into a clean static/ directory.
###############################################################################
FROM node:20-bookworm-slim AS frontend

WORKDIR /build

# Install JS deps first — cached unless package files change.
COPY front/package.json front/package-lock.json /build/front/
RUN cd /build/front && npm ci --no-audit --no-fund

# Copy front (webpack input/output) + static (other assets) + apps (Django
# templates and forms.py — Tailwind scans these via the `content` config in
# tailwind.config.js: `'../apps/**/*.html'`, `'../apps/**/forms.py'`, etc.
# Without apps/ here, the compiled CSS is missing every class only used in
# Django templates, which silently breaks the dashboard UI.
COPY front/ /build/front/
COPY static/ /build/static/
COPY apps/ /build/apps/

RUN cd /build/front && NODE_ENV=production npm run build

###############################################################################
# Stage 2 — Python build (compile uWSGI, PyMuPDF, cairosvg, lxml).
# Produces a virtualenv we copy into the runtime stage. Build tooling stays here.
###############################################################################
FROM python:3.11-slim-bookworm AS python-build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libsqlite3-mod-spatialite \
        libproj-dev \
        libgdal-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Build into an isolated venv so the runtime stage only inherits site-packages.
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY requirements.txt requirements.lock /tmp/
RUN pip install -U pip && \
    pip install -r /tmp/requirements.txt && \
    pip install uwsgi

###############################################################################
# Stage 3 — runtime
# Only runtime libraries + the virtualenv + app code + collected static files.
###############################################################################
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/venv/bin:$PATH

# Runtime system deps only — no compilers, no headers.
# spatialite/gdal/proj must stay at the same major version as the build stage.
# libcairo2 is required at import time by the exercise plugin (cairosvg→cairocffi
# dlopens libcairo.so.2); core/settings.py auto-imports every plugin in
# tanzawa_plugin/ so this must ship regardless of which plugins are enabled.
# rsync is used by bootstrap.sh to refresh the shared static volume on each boot.
RUN apt-get update && apt-get install -y --no-install-recommends \
        spatialite-bin \
        libsqlite3-mod-spatialite \
        libproj25 \
        libgdal32 \
        libcairo2 \
        curl \
        rsync \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy the pre-built virtualenv.
COPY --from=python-build /opt/venv /opt/venv

WORKDIR /app

# Application code.
COPY apps/ /app/apps/

# Stage 1 already laid host static/ + webpack output into /build/static — bring it across whole.
COPY --from=frontend /build/static/ /app/static/

# Themes (pre-built static CSS lives next to each theme; settings.py auto-discovers via THEMES_ROOT).
COPY front/src/themes/ /app/front/src/themes/

# Static is collected to a path that is NOT the docker-compose volume mount.
# bootstrap.sh rsyncs from here to /app/staticfiles (the mount) on every boot,
# so a `docker compose up --build` after a CSS change actually ships the new
# CSS to users — Docker named volumes ignore image content once populated.
#
# settings.py reads SECRET_KEY at import time, even for `collectstatic`.
# The real key comes from `.env` at runtime.
ENV STATIC_ROOT=/app/staticfiles-image \
    SECRET_KEY=build-only-not-used-at-runtime \
    DEBUG=False \
    ALLOWED_HOSTS=localhost

RUN mkdir -p /app/staticfiles-image /app/staticfiles && \
    cd /app/apps && python manage.py collectstatic --noinput

# Entrypoint: migrate + (optional) bootstrap superuser + uWSGI.
COPY deploy/bootstrap.sh /usr/local/bin/bootstrap.sh
RUN chmod +x /usr/local/bin/bootstrap.sh

EXPOSE 8000

# Caddy fronts the app, but a container-level healthcheck still helps compose
# report meaningful state. /auth/login/ is the unauthenticated 200 path.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/auth/login/ -o /dev/null || exit 1

CMD ["/usr/local/bin/bootstrap.sh"]
