from typing import List

from data.settings import models as settings_models
from django.conf import settings


def get_theme_choices() -> List[List[str]]:
    """
    This function returns all themes available to Tanzawa.
    """
    choices = [["", "Tanzawa"]]
    return choices + [[theme, theme.title()] for theme in settings.THEMES]


def get_site_settings() -> settings_models.MSiteSettings:
    """
    Get user configurable site settings.
    """
    return settings_models.MSiteSettings.objects.first() or settings_models.MSiteSettings()
