from django import apps
from django.conf import settings

from . import activation

_initial_load = True


class PluginsConfig(apps.AppConfig):
    name = "data.plugins"

    def ready(self):
        global _initial_load

        if _initial_load and settings.PLUGINS_RUN_MIGRATIONS_STARTUP:
            _initial_load = False
            from . import pool

            for plugin in pool.plugin_pool.enabled_plugins():
                activation.activate_plugin(plugin)
