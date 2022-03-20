# Getting Started

Tanzawa is a blogging system designed for the [IndieWeb](https://indieweb.org/) that focuses on sustainability.


## Requirements

Running Tanzawa outside of Docker requires the following:

* Python 3.9
* Spatalite (Geo-enabled SQLite) or Postgres with PostGIS enabled. We recommend Spatalite for most blogs.

If you are running Tanzawa outside of Docker, refer to the [GeoDjango installation documentation](https://docs.djangoproject.com/en/3.2/ref/contrib/gis/install/) for setting up the appropriate environment.


## Prepare Docker Image
```
$ git clone git@github.com:jamesvandyne/tanzawa.git
$ cd tanzawa
$ docker image build . -t tanzawa
```

Prepare your .env file and generate a secure secret key and append it to your .env file 

```
$ cp .env.sample .env
$ python3 -c "import secrets; print(secrets.token_urlsafe())" | xargs -I{} -n1 echo SECRET_KEY={} >> .env
```

Edit the `DOMAIN_NAME` setting in your .env file to match the domain where you'll be running Tanzawa.


## First Run

Start a container and open a shell.

```
$ docker run --rm -p 8000:8000 -v $PWD:/app -it tanzawa bash
```

### Prepare the database and create your user account

```
$ cd /app
$ python3 apps/manage.py migrate
$ python3 apps/manage.py createsuperuser
```

### Running the Development Web server

From inside the container, start the Django development server.

```
$ python3 apps/manage.py runserver 0.0.0.0:8000
```

Confirm you can login using your account by opening the Tanzawa Dashboard at [https://127.0.0.1:8000/a/]().
