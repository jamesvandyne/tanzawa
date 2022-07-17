import importlib
import logging
import os
import signal
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
    # Prevents AppRegistryNotReady errors during start up.
    from data.plugins.plugin import Plugin


logger = logging.getLogger(__name__)

WAIT_FOR_APP_REGISTRY_MAX = 15


class WaitForAppRegistryTimeExceeded(Exception):
    """Django app registry process has taken too long"""


def install_app(app_path: str) -> None:
    """
    Install an app into our settings.INSTALLED_APPS
    """
    # Prevent our plugins from being loaded twice.
    if _is_plugin(app_path) and not _is_installed(app_path):
        settings.INSTALLED_APPS += (app_path,)
        apps.app_configs = OrderedDict()
        apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
        apps.clear_cache()
        apps.populate(settings.INSTALLED_APPS)


def _is_plugin(app_path: str) -> bool:
    """
    Plugins must be located in the tanzawa_plugin module.
    """
    return app_path.startswith("tanzawa_plugin")


def _is_installed(app_path: str) -> bool:
    """
    Return if a module (exact match) or an AppConfig within a plugin is installed.
    """
    return any([app_path in installed for installed in settings.INSTALLED_APPS])


def activate_plugin(plugin: "Plugin") -> None:
    """
    Activates a plugin in Tanzawa.

    This will enable any URLs it has defined and run migrations.
    """
    install_app(plugin.plugin_module)
    _run_migrations(plugin=plugin)
    _reload_urlconf()
    utils.get_app_template_dirs.cache_clear()


def restart_parent_process() -> None:
    """After enabling or disabling a plugin we must gracefully restart our server process."""
    logger.info("Restarting requested from %s", os.getpid())
    # Don't restart if we're running under the develop server
    if sys.argv[1] != "runserver":
        os.kill(os.getppid(), signal.SIGHUP)


def deactivate_plugin(plugin: "Plugin") -> None:
    """
    Deactivates a plugin in Tanzawa.

    This will remove any URLs a plugin has added to the URL tree.
    """
    _reload_urlconf()
    utils.get_app_template_dirs.cache_clear()


def _reload_urlconf(urlconf=None) -> None:
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        clear_url_caches()
        importlib.reload(sys.modules[urlconf])


def _wait_for_app_registry():
    apps_ready = False
    models_ready = False
    time_waiting = 0.0

    # Wait for Django to finish populating the app registry up.
    while not apps_ready and not models_ready:
        try:
            apps.check_apps_ready()
            apps.check_models_ready()
        except exceptions.AppRegistryNotReady:
            if time_waiting > WAIT_FOR_APP_REGISTRY_MAX:
                raise WaitForAppRegistryTimeExceeded("App startup is taking too long.")
            sleep_time = 0.5
            time_waiting += sleep_time
            time.sleep(sleep_time)
            continue
        else:
            apps_ready = True
            models_ready = True


def _run_migrations(*, plugin: "Plugin") -> None:
    _wait_for_app_registry()

    # Run migrations.
    if plugin.has_migrations and not getattr(migrations, "MIGRATION_OPERATION_IN_PROGRESS", False):
        app_name = plugin.plugin_module.split(".")[-1]
        management.call_command("migrate", app_name, interactive=False)
