from plugins.core import Plugin

from django.utils import timezone


class CurrentTimePlugin(Plugin):
    """Displays the current time local time in the top navigation"""

    name = "Localtime"
    description = "Display the current local time in the top nav"
    identifier = "blog.tanzawa.plugins.time"

    @property
    def has_public_top_nav(self):
        return True

    def public_top_nav_icon(self) -> str:
        """Return an emoji that will be displayed next to the top nav item."""
        return "⏰"

    def public_top_nav_content(self) -> str:
        """Return html to be output on the page after the top nav icon"""
        return timezone.localtime().strftime("%H:%m")


def get_plugin():
    return CurrentTimePlugin()
