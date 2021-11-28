from operator import attrgetter
from typing import Iterable, Optional

from django.core import exceptions
from django.utils.module_loading import autodiscover_modules
from plugins.application import activation
from plugins.models import MPlugin

from . import plugin


class PluginPool:
    def __init__(self):
        self.plugins = {}
        self.discovered = False

    def _clear_cached(self) -> None:
        if "registered_plugins" in self.__dict__:
            del self.__dict__["registered_plugins"]

    def discover_plugins(self) -> None:

        if self.discovered:
            return

        autodiscover_modules("tanzawa_plugin")
        for plugin_ in self.plugins.values():
            activation.install_app(plugin_.plugin_module)
        self.discovered = True

    def get_all_plugins(self) -> Iterable[plugin.Plugin]:
        self.discover_plugins()
        plugins = sorted(self.plugins.values(), key=attrgetter("name"))
        return plugins

    def get_plugin(self, identifier) -> Optional[plugin.Plugin]:
        self.discover_plugins()

        for plugin_ in self.plugins.values():
            if plugin_.identifier == identifier:
                return plugin_
        return None

    def register_plugin(self, plugin_: plugin.Plugin) -> plugin.Plugin:
        if not issubclass(plugin_.__class__, plugin.Plugin):
            raise exceptions.ImproperlyConfigured("Tanzawa Plugins must be subclasses of Plugin, %r is not." % plugin)
        plugin_name = plugin_.name
        self.plugins[plugin_name] = plugin_
        return plugin_

    def enable(self, plugin_: plugin.Plugin) -> None:
        """
        Marks a plugin as enabled before activating it.
        """
        if MPlugin.objects.filter(identifier=plugin_.identifier).exists():
            MPlugin.objects.filter(identifier=plugin_.identifier).update(enabled=True)
        else:
            MPlugin.new(identifier=plugin_.identifier, enabled=True)
        activation.activate_plugin(plugin_)

    def disable(self, plugin_: plugin.Plugin) -> None:
        """
        Marks a plugin as disabled before deactivating it.
        """
        if MPlugin.objects.filter(identifier=plugin_.identifier).exists():
            MPlugin.objects.filter(identifier=plugin_.identifier).update(enabled=False)
        else:
            MPlugin.new(identifier=plugin_.identifier, enabled=False)
        activation.deactivate_plugin(plugin_)

    def urls(self) -> Iterable[str]:
        """
        Yields the import path to urls.py for each enabled plugin.
        """
        for plugin_ in self.enabled_plugins():
            if plugin_.urls:
                yield plugin_.urls

    def admin_urls(self) -> Iterable[str]:
        """
        Yields the import path to admin_urls.py for each enabled plugin.
        """
        for plugin_ in self.enabled_plugins():
            if plugin_.admin_urls:
                yield plugin_.admin_urls

    def enabled_plugins(self) -> Iterable[plugin.Plugin]:
        """
        Yields enabled Plugin instances
        """
        self.discover_plugins()
        enabled = MPlugin.objects.enabled().values_list("identifier", flat=True)
        for plugin_ in self.plugins.values():
            if plugin_.identifier in enabled:
                yield plugin_


plugin_pool = PluginPool()
