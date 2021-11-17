import importlib
import sys

from django.conf import settings
from django.urls import clear_url_caches
from plugins.core import Plugin


def _reload_urlconf(urlconf=None):
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        clear_url_caches()
        importlib.reload(sys.modules[urlconf])


def activate_plugin(plugin: Plugin) -> None:
    """
    Activates a plugin in Tanzawa.

    This will enable any URLs it has defined and run migrations.
    """
    _reload_urlconf()


def deactivate_plugin(plugin: Plugin) -> None:
    """
    Deactivates a plugin in Tanzawa.

    This will remove any URLs a plugin has added to the URL tree.
    """
    _reload_urlconf()
