import abc
from typing import TYPE_CHECKING, Optional, Protocol

from django import http, urls
from django.conf import settings

if TYPE_CHECKING:
    from data.post import models as post_models


class NavigationProtocol(Protocol):
    @property
    def has_public_top_nav(self) -> bool:
        """
        Does this plugin have public facing top nav?
        """
        return False

    @property
    def has_admin_left_nav(self) -> bool:
        """
        Return if the plugin has left navigation in admin pages.
        """
        return False


class FeedHook(Protocol):
    @property
    def has_feed_hooks(self) -> bool:
        """
        Plugins which use the the feed hook should return True
        """
        return False

    def feed_before_content(self, request: http.HttpRequest, post: Optional["post_models.TPost"] = None) -> str:
        """
        Returns any content that should be displayed before the post.
        """
        return ""

    def feed_after_content(self, request: http.HttpRequest, post: Optional["post_models.TPost"] = None) -> str:
        """
        Returns any content that should be displayed after the post.
        """
        return ""


class Plugin(abc.ABC, NavigationProtocol, FeedHook):
    name: str
    description: str
    # A unique namespaced identifier for the plugin
    identifier: str
    settings_url_name: str = ""

    def is_enabled(self) -> bool:
        from .models import MPlugin

        return (
            MPlugin.objects.filter(identifier=self.identifier).values_list("enabled", flat=True).first()
            or self.identifier in settings.FORCE_ENABLED_PLUGINS
            or False
        )

    @property
    def plugin_module(self) -> str:
        """Return the python module path to the plugin's module"""
        return ".".join(self.__module__.split(".")[:-1])

    @property
    def settings_url(self) -> str:
        """
        The main URL for configuring the plugin.

        Plugins should define the settings_url_name attribute if they can be configured.
        """
        try:
            return urls.reverse(self.settings_url_name)
        except urls.NoReverseMatch:
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
    def urls(self) -> str | None:
        """Return the path to the _public_ url configuration for a plugin"""
        # TODO: Make this check for a urls.py and return None if not exists
        return f"{self.plugin_module}.urls"

    @property
    def admin_urls(self) -> str | None:
        """Return the path to the _admin_ url configuration for a plugin"""
        return f"{self.plugin_module}.admin_urls"
