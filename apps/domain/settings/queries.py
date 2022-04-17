from typing import List

from django.conf import settings


def get_theme_choices() -> List[List[str]]:
    """
    This function returns all themes available to Tanzawa.
    """
    choices = [["", "Tanzawa"]]
    return choices + [[theme, theme.title()] for theme in settings.THEMES]
