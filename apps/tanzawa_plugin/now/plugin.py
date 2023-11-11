from django import template
from django.template.loader import render_to_string

from data.plugins import plugin, pool

__identifier__ = "blog.tanzawa.plugins.nowpage"


class NowPlugin(plugin.Plugin):
    """Give your site a now page."""

    name = "Now"
    identifier = __identifier__
    settings_url_name = "plugin_now_admin:update_now"

    @property
    def description(self):
        return render_to_string("now/description.html")

    @property
    def has_public_top_nav(self):
        return True

    def render_navigation(
        self,
        *,
        context: template.Context,
        render_location: str,
    ) -> str:
        """Render the public facing navigation menu item."""
        t = context.template.engine.get_template("now/navigation.html")
        return t.render(context=context)


def get_plugin() -> plugin.Plugin:
    return NowPlugin()


pool.plugin_pool.register_plugin(get_plugin())
