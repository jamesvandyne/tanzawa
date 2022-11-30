# Deploying Tanzawa

Hosting your Tanzawa instance with Fly.io is the easiest and recommended way to use Tanzawa.

To get started, first create a new app in Fly.io in whichever region is closest to you. Tanzawa does not use PostgresSQL, so there is no need to create a database if prompted.

## Create a volume

Create a volume to store your database and file uploads. The region should be the same as your app.
 
```
$ flyctl volumes create my_volume_name --region nrt --size 3
```

## Set Secrets

Tanzawa requires a few secrets to be set in order to operate. Set them using the commands below.

If you have multiple domains you want to access your blog from include them both with a comma separating them. e.g. `ALLOWED_HOSTS=hello.fly.dev,example.com,www.example.com`. 

```
$ flyctl secrets set ALLOWED_HOSTS=<your_domain>
$ flyctl secrets set DB_NAME=/opt/tanzawa/data/db.sqlite3
$ flyctl secrets set MEDIA_ROOT=/opt/tanzawa/data/media/
```

## Deploy 

Deploying Tanzawa to Fly.io using the deploy command.

```
$ flyctl deploy
```


## Create a user

Creating a user will allow you to login to Tanzawa and write blog posts.

```
$ flyctl ssh console
$ cd /app/apps
$ python manage.py createsuperuser
```

Once created you should be able to login at http://my_app.fly.dev/a/ where my_app is the name of your application.

# Migrate an existing install Tanzawa to Fly

To migrate an existing installation of Tanzawa to Fly.io you only need to copy your SQLite database and media files the volume.

You can do this using the `ssh sftp` utility in the flyctl app.

```
$ flyctl ssh sftp shell
>> put /Users/my_user/backup/db.sqlite3 /opt/tanzawa/data/sqlite3
>> put /Users/my_user/backup/media /opt/tanzawa/data/media
```
