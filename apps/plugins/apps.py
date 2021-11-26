from django import apps
from plugins.application import activation
from django.conf import settings

_initial_load = True


class PluginsConfig(apps.AppConfig):
    name = "plugins"

    def ready(self):
        global _initial_load
        if _initial_load and settings.PLUGINS_RUN_MIGRATIONS_STARTUP:
            _initial_load = False
            from plugins.core import plugin_pool

            for plugin in plugin_pool.enabled_plugins():
                activation.activate_plugin(plugin)
