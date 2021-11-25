import importlib
import sys
import time
from collections import OrderedDict
from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from django.core import exceptions, management
from django.db import migrations
from django.template import utils
from django.urls import clear_url_caches

if TYPE_CHECKING:
    from plugins.core import Plugin


def _reload_urlconf(urlconf=None) -> None:
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        clear_url_caches()
        importlib.reload(sys.modules[urlconf])


def _install_app(plugin: "Plugin", app_path: str) -> None:
    app_name = app_path.split(".")[-1]
    apps_ready = False
    models_ready = False

    # Prevent our plugins from being loaded twice.
    if app_path not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS += (app_path,)
        apps.app_configs = OrderedDict()
        apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
        apps.clear_cache()
        apps.populate(settings.INSTALLED_APPS)

    # Wait for Django to finish starting up.
    while not apps_ready and not models_ready:
        try:
            apps.check_apps_ready()
            apps.check_models_ready()
        except exceptions.AppRegistryNotReady:
            time.sleep(0.5)
            continue
        else:
            apps_ready = True
            models_ready = True

    # Run migrations.
    if plugin.has_migrations and not getattr(migrations, "MIGRATION_OPERATION_IN_PROGRESS", False):
        management.call_command("migrate", app_name, interactive=False)


def _uninstall_app(app_name: str) -> None:
    apps.app_configs = OrderedDict()
    apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
    apps.clear_cache()
    apps.populate(settings.INSTALLED_APPS)


def activate_plugin(plugin: "Plugin") -> None:
    """
    Activates a plugin in Tanzawa.

    This will enable any URLs it has defined and run migrations.
    """
    _install_app(plugin, plugin.plugin_module)
    _reload_urlconf()
    utils.get_app_template_dirs.cache_clear()


def deactivate_plugin(plugin: "Plugin") -> None:
    """
    Deactivates a plugin in Tanzawa.

    This will remove any URLs a plugin has added to the URL tree.
    """
    _reload_urlconf()
    _uninstall_app(plugin.plugin_module)
