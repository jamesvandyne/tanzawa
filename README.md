# Tanzawa

Tanzawa is a blogging system designed for the [IndieWeb](https://indieweb.org/) that focuses on sustainability.


## Installation

We recommend using a fully managed host like Fly.io when running Tanzawa. There are [setup instructions](https://jamesvandyne.github.io/tanzawa/deployment/) in the deployment documentation.

## Development

The simplest way to run Tanzawa locally is in a Docker container.

Running Tanzawa outside of Docker requires the following:

* Python 3.10 or higher
* Spatalite (Geo-enabled SQLite)

Please refer to the [GeoDjango installation documentation](https://docs.djangoproject.com/en/3.2/ref/contrib/gis/install/) for setting up the appropriate environment.


### Running Tanzawa Locally

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

### First Run

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

Run Development Web server

```
$ python3 apps/manage.py runserver 0.0.0.0:8000
```

Confirm you can login using your account by opening the Tanzawa Dashboard at [https://127.0.0.1:8000/a/]().


## Customizing Tanzawa

### Site Name

1. Visit the Django Settings by visiting `/admin/` or opening the Tanzawa Dashboard and clicking `Settings`.
2. Click the "Site Settings" and add a record.

### Add Streams / Modifying the Navigation

Streams are how you categorize posts in Tanzawa. By default Tanzawa creates streams to covert most basic IndieWeb content types.

1. Open the Django Settings in your browser  `/admin/`
2. Click add stream and fill in the form as you wish.
   1. Icon: Input an emoji of your choice.
   2. Name: This will appear on the left as navigation.
   3. Slug: Generally this is the name in lowercase and will appear in stream urls e.g. `example.com/notes`

## Sites using Tanzawa

Is your site running Tanzawa? Open a pull request and add your site below.

* [James Van Dyne](https://jamesvandyne.com)
* [Ricardo Mendes](https://blog.rmendes.net)
