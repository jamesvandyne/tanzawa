from plugins import core

__description__ = "Give your site a now page."
__identifier__ = "blog.tanzawa.plugins.nowpage"


class NowPlugin(core.Plugin):
    """Give your site a now page."""

    name = "Now"
    description = __description__
    identifier = __identifier__

    @property
    def has_public_top_nav(self):
        return True

    def public_top_nav_icon(self) -> str:
        """Return an emoji that will be displayed next to the top nav item."""
        return "🔛"

    def public_top_nav_content(self) -> str:
        """Return html to be output on the page after the top nav icon"""
        return "Now"


def get_plugin() -> core.TanzawaPlugin:
    return NowPlugin()


core.plugin_pool.register_plugin(get_plugin())
