from operator import attrgetter

from typing import Iterable
from django.utils.module_loading import autodiscover_modules


from plugins.application import activation
from plugins.core import Plugin
from plugins.models import MPlugin


class PluginPool:
    def __init__(self):
        self.plugins = {}
        self.discovered = False
        self.registery = {}

    def _clear_cached(self):
        if "registered_plugins" in self.__dict__:
            del self.__dict__["registered_plugins"]

    def discover_plugins(self):

        if self.discovered:
            return

        autodiscover_modules("tanzawa_plugin", register_to=self.registery)
        self.discovered = True

    def get_all_plugins(self):
        self.discover_plugins()
        plugins = sorted(self.plugins.values(), key=attrgetter("name"))
        return plugins

    def get_plugin(self, identifier):
        self.discover_plugins()

        for plugin in self.plugins.values():
            if plugin.identifier == identifier:
                return plugin
        return None

    def register_plugin(self, plugin):

        # TODO: Add class validation
        # if not issubclass(plugin, CMSPluginBase):
        #     raise ImproperlyConfigured(
        #         "CMS Plugins must be subclasses of CMSPluginBase, %r is not."
        #         % plugin
        #     )
        plugin_name = plugin.name
        # if plugin_name in self.plugins:
        #     raise PluginAlreadyRegistered(
        #         "Cannot register %r, a plugin with this name (%r) is already "
        #         "registered." % (plugin, plugin_name)
        #     )

        plugin.value = plugin_name
        self.plugins[plugin_name] = plugin
        return plugin

    def enable(self, plugin: Plugin):
        """
        Marks a plugin as enabled before activating it.
        """
        if MPlugin.objects.filter(identifier=plugin.identifier).exists():
            MPlugin.objects.filter(identifier=plugin.identifier).update(enabled=True)
        else:
            MPlugin.new(identifier=plugin.identifier, enabled=True)
        activation.activate_plugin(plugin)

    def disable(self, plugin: Plugin):
        """
        Marks a plugin as disabled before deactivating it.
        """
        if MPlugin.objects.filter(identifier=plugin.identifier).exists():
            MPlugin.objects.filter(identifier=plugin.identifier).update(enabled=False)
        else:
            MPlugin.new(identifier=plugin.identifier, enabled=False)
        activation.deactivate_plugin(plugin)

    def urls(self) -> Iterable[str]:
        """
        Yields the import path to urls.py for each enabled plugin.
        """
        for plugin in self.enabled_plugins():
            if plugin.urls:
                yield plugin.urls

    def enabled_plugins(self) -> Iterable[Plugin]:
        """
        Yields enabled Plugin instances
        """
        self.discover_plugins()
        enabled = MPlugin.objects.enabled().values_list("identifier", flat=True)
        for plugin in self.plugins.values():
            if plugin.identifier in enabled:
                yield plugin


plugin_pool = PluginPool()
