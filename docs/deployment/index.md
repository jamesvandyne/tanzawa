:wqUsing Tanzawa in Production

The instructions for running Tanzawa in the README are for demonstration and development purposes. Using the Django `runserver` is not recommended in production use for your blog.

This document will guide you through how to setup Tanzawa on your own server. There are two different methods described: running directly on the server and using Docker.

## Requirements

 This  guide assumes a modern Ubuntu LTS version of the OS is being used. As Tanzawa is python application, running it in production requires 2 servers:

1. uWSGI – this is what runs the actual Tanzawa code. Currently you can also use Gunicorn, but the project will be switching to uWSGI in the near future.
2. Nginx or Apache – this is used for two purposes:
   1. Serving all staticfiles (javascript, css, images) and media files (user uploads).
   2. Proxying all requests that _aren't_ staticfiles to the uWSGI server.
   
## Docker

This section will guide you through installing ngix and configuring Tanzawa via Docker using `docker compose`. `$` is denotes a regular shell.

### Component Paths

This guide will assume that the Tanzawa data will live in `/opt/tanzawa/`.

|Component|Path|Notes|
|---|---|---|
|database|/opt/tanzawa/db.sqlite3|
|file uploads|/opt/tanzawa/media/|
|plugins|/opt/tanzawa/plugins/|
|themes|/opt/tanzawa/themes/|
|static resources|/opt/tanzawa/staticfiles|Publicly accessible by nginx|
|tanzawa socket|/var/run/tanzawa/tanzawa.sock||
|server name config|/opt/tanzawa/server_name|Used to configure the domain by nginx|


#### Base setup

First, install nginx and base packages required to install Docker.

```
$ apt-get update && apt-get install -y apt-utils nginx certbot apt-transport-https ca-certificates curl gnupg lsb-release python3-pip
```

Add Docker GPG key, so you can install the Docker packages.

```
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

Add the docker repository.

```
$ echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \

$ apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io && apt-get upgrade -y
```

Install docker-compose and add the command and link it so it's executable in your path. 

```
$ pip3 install docker-compose
$ ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

### docker-compose.yml

Copy the following YAML file to `/opt/tanzawa/docker-compose.yml`. This is the main file that will setup the Docker container running Tanzawa.

```yaml
version: "3.9"

services:
  web:
    image: jamesvandyne/tanzawa
    restart: always
    volumes:
      - /opt/tanzawa/staticfiles:/opt/tanzawa/static
      - /var/run/tanzawa:/var/run/tanzawa
      - /opt/tanzawa/data:/opt/tanzawa/data
    environment:
      - ENV_FILE=/opt/tanzawa/data/env
```

Note that there are no open ports in this docker-compose configuration. That's because the default Tanzawa image is accessible via a socket located in `/var/run/tanzawa/tanzawa.sock`.

### nginx

If it doesn't exist already create the directories to house your nginx configurations.

```
$ mkdir -p /etc/nginx/sites-available/ /etc/nginx/sites-enabled
```

### uWSGI/ngix

Add a file to store our uWSGI specific nginx configuration in `/etc/nginx/usgi_params` with the following contents:

```
uwsgi_param  QUERY_STRING       $query_string;
uwsgi_param  REQUEST_METHOD     $request_method;
uwsgi_param  CONTENT_TYPE       $content_type;
uwsgi_param  CONTENT_LENGTH     $content_length;

uwsgi_param  REQUEST_URI        $request_uri;
uwsgi_param  PATH_INFO          $document_uri;
uwsgi_param  DOCUMENT_ROOT      $document_root;
uwsgi_param  SERVER_PROTOCOL    $server_protocol;
uwsgi_param  REQUEST_SCHEME     $scheme;
uwsgi_param  HTTPS              $https if_not_empty;

uwsgi_param  REMOTE_ADDR        $remote_addr;
uwsgi_param  REMOTE_PORT        $remote_port;
uwsgi_param  SERVER_PORT        $server_port;
uwsgi_param  SERVER_NAME        $server_name;
```


Add a file that will house the `server_name` configuration for your nginx configuration. Replace `mydomain.com` with the domain you plan to run Tanzawa.

```
$ echo "server_name mydomaim.com" >> /opt/tanzawa/server_name
```


Create a nginx configuration file for Tanzawa in `/etc/nginx/sites-available/tanzawa.conf` with the following content:

```
# the upstream component nginx needs to connect to
upstream django {
    server unix:///var/run/tanzawa/tanzawa.sock;
}

# configuration of the server
server {
    # the port your site will be served on
    listen      80;
    # the domain name it will serve for
    include /opt/tanzawa/server_name;
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;

    # Django media
    location /media  {
        alias /opt/tanzawa/media;
    }

    location /static {
        alias /opt/tanzawa/staticfiles; # your Django project's static files - amend as required
    }

    # Finally, send all non-media requests to the Django server.
    location / {
        uwsgi_pass  django;
        include     /etc/nginx/uwsgi_params; # the uwsgi_params file you installed
    }
}
```

Enable Tanzawa nginx configuration and disable the default site.

```
$ ln -s /etc/nginx/sites-available/tanzawa.conf /etc/nginx/sites-enabled/
$ unlink /etc/nginx/sites-enabled/default
```

## Setup Tanzawa environment settings

These are the core settings that are used to configure the Django installation. Any changes to this file will require a restart of Tanzawa to take effect. Save this file in `/opt/tanzawa/data/env`.

```
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost

# set to False if running over http
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

DATABASE_URL=sqlite:////opt/tanzawa/data/db.sqlite3
DATABASE_ENGINE=django.contrib.gis.db.backends.spatialite

# Used to configure Django error messages
LANGUAGE_CODE=en-us

# Which timezone is your blog running?
TIME_ZONE=UTC

# Collect static/media in the project root.
STATIC_ROOT=/opt/tanzawa/static/
MEDIA_ROOT=/opt/tanzawa/data/media/
```
Add a unique `SECRET_KEY` to the env file above by running the following command.

```
$ python3 -c "import secrets; print(secrets.token_urlsafe())" | xargs -I{} -n1 echo SECRET_KEY={} >> /opt/tanzawa/data/env
```
## Setup Weekly Security Updates

Keeping your server updated with the latest security patches is important. While not technically related to Tanzawa, it's a good practice. Put the following file in `/etc/cron.weekly/weekly_update.sh`

```bash
 #!/bin/bash
apt-get update
apt-get upgrade -y
apt-get autoclean
```

Modify permissions it's fully executable to enable.
```
$ chmod 755 /etc/cron.weekly/weekly_update.sh
```