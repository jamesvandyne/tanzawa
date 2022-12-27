from django import template

from data.plugins import plugin, pool

__identifier__ = "blog.tanzawa.plugins.exercise"


class ExercisePlugin(plugin.Plugin):
    """Track your runs and rides."""

    name = "Exercise"
    identifier = __identifier__

    @property
    def description(self) -> str:
        return "Track your runs and rides on your site."

    @property
    def has_public_top_nav(self):
        return True

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
        t = context.template.engine.get_template("exercise/navigation.html")
        return t.render(context=context)


def get_plugin() -> plugin.Plugin:
    return ExercisePlugin()


pool.plugin_pool.register_plugin(get_plugin())
