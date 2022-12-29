# Exercise

The exercise plugin is a core plugin of Tanzawa. It allows you to import your activity data from Strava.
Once enabled there will be a button in the admin exercise dashboard (`/a/exercise/`) that will download
the latest activities.

## Strava Setup

Tanzawa requires API access in order to access your Strava data. This
requires you to https://strava.com/settings/api in your [Strava account settings](https://strava.com/settings/api).

Once created set the `client id` and `client secret` values in Tanzawa.

```
$ flyctl secrets set STRAVA_CLIENT_ID=your_client_id
$ flyctl secrets set STRAVA_CLIENT_SECRET=your_client_secret
```

## Importing all activities

If you have more than 30 activities in Strava, they will need to be imported by running a command.
This needs to be run after importing activities from the website once, so your Tanzawa has authorization to access your account. 

```
$ flyctl ssh console
$ cd app
$ python apps/manage.py import_all_strava_activities
```