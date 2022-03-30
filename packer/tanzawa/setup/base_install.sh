# Install system deps
apt-get update
apt-get upgrade -y
# Backend deps
apt-get install -y spatialite-bin libsqlite3-mod-spatialite binutils libproj-dev gdal-bin nodejs npm


# Clone latest version of Tanzawa
git clone https://github.com/jamesvandyne/tanzawa.git /opt/tanzawa/tanzawa/

# Move uwsgi configuration to the appropriate location
mkdir -p /etc/uwsgi/vassals/
mv /tmp/uwsgi.ini /etc/uwsgi/vassals/tanzawa.ini

# Setup directories
mkdir -p /var/run/tanzawa/
mkdir -p /opt/tanzawa/data/
mkdir -p /opt/tanzawa/static/
mkdir -p /opt/tanzawa/data/media/
chown www-data:www-data /var/run/tanzawa/
chown www-data:www-data /opt/tanzawa/data/
chown www-data:www-data /opt/tanzawa/data/media/

# Install Python deps
pip install -U pip
pip install uwsgi
pip install -r /opt/tanzawa/tanzawa/requirements_dev.txt
rm -rf /var/lib/apt/lists/*


# Prepare env file
# TODO: This should be fed in by Docker / not rely on the .env file
python3 -c "import secrets; print(secrets.token_urlsafe())" | xargs -I{} -n1 echo SECRET_KEY={} >> /tmp/env
mv /tmp/env /opt/tanzawa/data/env


# Install frontend deps
cd /opt/tanzawa/tanzawa/front
npm install

# Build production assets
npm run build

# Collect static
cd /opt/tanzawa/tanzawa/
python3 apps/manage.py collectstatic --noinput