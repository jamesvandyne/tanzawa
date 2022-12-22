from django import template

from data.plugins import plugin, pool

__identifier__ = "blog.tanzawa.plugins.health"


class HealthPlugin(plugin.Plugin):
    """Track your health."""

    name = "Health"
    identifier = __identifier__

    @property
    def description(self) -> str:
        return "Track your health on your site."

    @property
    def has_admin_left_nav(self) -> bool:
        return True

    def render_navigation(
        self,
        *,
        context: template.Context,
        render_location: str,
    ) -> str:
        """
        Render the admin navigation menu item.
        """
        t = context.template.engine.get_template("health/navigation.html")
        return t.render(context=context)


def get_plugin() -> plugin.Plugin:
    return HealthPlugin()


pool.plugin_pool.register_plugin(get_plugin())
