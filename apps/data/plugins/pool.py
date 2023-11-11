from collections.abc import Iterable
from operator import attrgetter

from django.conf import settings
from django.core import exceptions
from django.db import utils
from django.utils.module_loading import autodiscover_modules

from data.plugins import plugin


def _get_m_plugin():
    """
    Only import django models when they're used to prevent raising AppRegistryNotReady errors.
    """
    from data.plugins.models import MPlugin

    return MPlugin


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

        autodiscover_modules("plugin")

        self.discovered = True

    def get_all_plugins(self) -> Iterable[plugin.Plugin]:
        self.discover_plugins()
        plugins = sorted(self.plugins.values(), key=attrgetter("name"))
        return plugins

    def get_plugin(self, identifier) -> plugin.Plugin | None:
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
        MPlugin = _get_m_plugin()
        if MPlugin.objects.filter(identifier=plugin_.identifier).exists():
            MPlugin.objects.filter(identifier=plugin_.identifier).update(enabled=True)
        else:
            MPlugin.new(identifier=plugin_.identifier, enabled=True)

    def disable(self, plugin_: plugin.Plugin) -> None:
        """
        Marks a plugin as disabled before deactivating it.
        """
        MPlugin = _get_m_plugin()
        if MPlugin.objects.filter(identifier=plugin_.identifier).exists():
            MPlugin.objects.filter(identifier=plugin_.identifier).update(enabled=False)
        else:
            MPlugin.new(identifier=plugin_.identifier, enabled=False)

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
        MPlugin = _get_m_plugin()
        try:
            enabled = list(MPlugin.objects.enabled().values_list("identifier", flat=True))
        except utils.OperationalError:
            # MPlugin table hasn't been migrated yet
            return []
        enabled_plugins = []
        for plugin_ in self.plugins.values():
            if plugin_.identifier in enabled or plugin_.identifier in settings.FORCE_ENABLED_PLUGINS:
                # yield plugin_
                enabled_plugins.append(plugin_)
        return enabled_plugins

    def feed_plugins(self) -> Iterable[plugin.Plugin]:
        for enabled_plugin in self.enabled_plugins():
            if enabled_plugin.has_feed_hooks:
                yield enabled_plugin


plugin_pool = PluginPool()
