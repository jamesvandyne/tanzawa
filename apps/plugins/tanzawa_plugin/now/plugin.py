from django import urls
from django.template.loader import render_to_string
from plugins import plugin, pool

__identifier__ = "blog.tanzawa.plugins.nowpage"


class NowPlugin(plugin.Plugin):
    """Give your site a now page."""

    name = "Now"
    identifier = __identifier__

    @property
    def description(self):
        return render_to_string("now/description.html")

    @property
    def settings_url(self):
        return urls.reverse_lazy("plugin_now_admin:update_now")

    @property
    def has_public_top_nav(self):
        return True

    def public_top_nav_icon(self) -> str:
        """Return an emoji that will be displayed next to the top nav item."""
        return "👉"

    def public_top_nav_content(self) -> str:
        """Return html to be output on the page after the top nav icon"""
        return "Now"


def get_plugin() -> plugin.Plugin:
    return NowPlugin()


pool.plugin_pool.register_plugin(get_plugin())
