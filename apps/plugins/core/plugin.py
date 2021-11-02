from abc import abstractmethod
from typing import Protocol


class Plugin(Protocol):
    """"""

    name: str
    description: str
    # A unique namespaced identifier for the plugin
    identifier: str

    @property
    def public_has_top_nav(self) -> bool:
        """ Does this plugin have public facing top nav? """
        return False

    @abstractmethod
    def public_top_nav_icon(self) -> str:
        """Return an emoji that will be displayed next to the top nav item."""
        raise NotImplementedError

    @abstractmethod
    def public_top_nav_content(self) -> str:
        """Return html to be output on the page after the top nav icon"""
        raise NotImplementedError
