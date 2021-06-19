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

```

# Sites using Tanzawa

* [James Van Dyne](https://jamesvandyne.com)