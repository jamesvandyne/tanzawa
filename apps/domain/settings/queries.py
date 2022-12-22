from typing import List, Optional

from django.conf import settings

from data.settings import models as settings_models
from data.trips import models as trip_models


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


def get_active_trip() -> Optional[trip_models.TTrip]:
    """
    Get the active trip.
    """
    site_settings = get_site_settings()
    return site_settings.active_trip
