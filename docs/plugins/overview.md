# Plugins

Plugins allow you to create custom functionality for you Tanzawa website.
They can be selectively enabled and disabled.

Tanzawa Plugins are regular Django applications. They can provide:

* Custom URLs (public and admin facing)
* Database tables
* Navigation items in the header of public site 

## Activation / Deactivation

Plugins can be activated by clicking on the "Enable" button at `/a/plugins/`.

Alternatively you can enable them from the command line with the following command.

```
python3 apps/manage.py enable_plugin <identifier>
```

Likewise you can disable them by running the `disable_plugin` command. 

```
python3 apps/manage.py disable_plugin <identifier>
```


Refer to [Custom Plugins](custom-plugins.md) for a guide on writing your own plugins.