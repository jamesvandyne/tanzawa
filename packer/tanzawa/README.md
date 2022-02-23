# Tanzawa uWSGI

This packer configuration builds a Docker image that is acceptable to run in production environments.

## Paths

|Path|Description|
|---|---|
|/opt/tanzawa/|Tanzawa root install|
|/opt/tanzawa/tanzawa|Tanzawa app root|
|/var/run/tanzawa/tanzawa.sock|uWSGI server socket|
|/opt/tanzawa/data/db.sqlite3|Database|
|/opt/tanzawa/data/static/|Django staticfiles|
|/opt/tanzawa/data/media/|File uploads|
