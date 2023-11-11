import logging
from collections import OrderedDict

from django.apps import apps
from django.conf import settings

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
