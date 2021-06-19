# Tanzawa

Tanzawa is a blogging system designed for the [IndieWeb](https://indieweb.org/) that focuses on sustainability.

# Running Tanzawa

The simplest way to run try Tanzawa is to run it locally in a Docker container.

```
$ git clone git@github.com:jamesvandyne/tanzawa.git
$ cd tanzawa
$ docker image build -t tanzawa
$ cp .env.sample .env
# Generate a secure secret key and append it to your .env file 
$ python3 -c "import secrets; print(secrets.token_urlsafe())" | xargs -I{} -n1 echo SECRET_KEY={} >> .env
$ docker run --rm -p 8000:8000 -v $PWD:/app -it tanzawa bash

# Inside Container

$ cd /app

# Prepare Database
$ python3 apps/manage.py migrate

# Create your user account
$ python3 apps/manage.py createsuperuser
$ python3 apps/manage.py collectstatic

# Run Development Webserver
$ python3 apps/manage.py runserver 0.0.0.0:8000
```

# Sites using Tanzawa

* [James Van Dyne](https://jamesvandyne.com)