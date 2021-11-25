from django import apps
from plugins.application import activation

_initial_load = True


class PluginsConfig(apps.AppConfig):
    name = "plugins"

    def ready(self):
        global _initial_load
        if _initial_load:
            _initial_load = False
            from plugins.core import plugin_pool

            for plugin in plugin_pool.enabled_plugins():
                activation.activate_plugin(plugin)
