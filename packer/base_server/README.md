# Base Server

This is the packer configuration for a base Ubuntu server that will run a Tanzawa in a container.
It's designed to be used to create VMs that run as Digital Ocean droplets etc...

## Installs

The base server automatically installs the following packages

* Docker
* Nginx
* Certbot

## Configurations

This server is setup to automatically:

* Apply security patches _weekly_.
* Look for Tanzawa upgrades _daily_.


## Paths

The Tanzawa container is setup to store all data outside of the container.

|Component|Path|Notes|
|---|---|---|
|database|/opt/tanzawa/db.sqlite3|
|file uploads|/opt/tanzawa/media/|
|plugins|/opt/tanzawa/plugins/|
|themes|/opt/tanzawa/themes/|
|static resources|/opt/tanzawa/staticfiles|Publicly accessible by nginx|


## Variables

## Building

Build a new image.

```
$ packer build base_server.pkr.hcl
```

Format the packer configurations.

```
$ packer fmt .
```




