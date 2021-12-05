import abc
import pathlib
from importlib import util as importlib_util
from typing import Optional, Protocol

from plugins.models import MPlugin


class TopNavProtocol(Protocol):
    @property
    def public_has_top_nav(self) -> bool:
        """Does this plugin have public facing top nav?"""
        return False


class Plugin(abc.ABC, TopNavProtocol):
    name: str
    description: str
    # A unique namespaced identifier for the plugin
    identifier: str

    def is_enabled(self) -> bool:
        return MPlugin.objects.filter(identifier=self.identifier).values_list("enabled", flat=True).first() or False

    @property
    def plugin_module(self) -> str:
        """Return the python module path to the plugin's module"""
        return ".".join(self.__module__.split(".")[:-1])

    @property
    def settings_url(self) -> str:
        """The main URL for configuring the plugin.

        Plugins that do not provide any configuration via the admin should return a blank string.
        """
        return ""

    def render_navigation(
        self,
        *,
        context,
        render_location: str,
    ) -> str:
        """Render the public facing navigation menu item."""
        return ""

    @property
    def urls(self) -> Optional[str]:
        """Return the path to the _public_ url configuration for a plugin"""
        # TODO: Make this check for a urls.py and return None if not exists
        return f"{self.plugin_module}.urls"

    @property
    def admin_urls(self) -> Optional[str]:
        """Return the path to the _admin_ url configuration for a plugin"""
        return f"{self.plugin_module}.admin_urls"

    @property
    def has_migrations(self) -> bool:
        """Check if a plugin has migration directory.

        Uses pathlib instead of importlib to avoid importing modules.
        """
        module_spec = importlib_util.find_spec(self.__module__)
        if not module_spec or not module_spec.origin:
            return False

        migration_module = pathlib.Path(module_spec.origin).parent / "migrations"
        return migration_module.is_dir()
