import logging

from django import template

from data.plugins import plugin as plugin_base
from data.plugins import pool

register = template.Library()
logger = logging.getLogger(__name__)


class _RenderPlugin(template.Node):
    def __init__(self, *, plugin: template.Variable, render_location: str):
        self.plugin = plugin
        self.render_location = render_location[1:-1]  # trim quotes

    def _get_plugin(self, context) -> plugin_base.Plugin:
        plugin_variable = self.plugin.resolve(context=context)
        plugin_ = pool.plugin_pool.get_plugin(plugin_variable)
        if not plugin_:
            raise template.TemplateSyntaxError(f"Plugin with identifier {plugin_variable} does not exist.")
        if not plugin_.is_enabled():
            raise template.TemplateSyntaxError(f"Plugin {plugin_variable} is not enabled.")

        return plugin_

    def _get_context(self, context) -> dict:
        context["render_location"] = self.render_location
        return context

    def _render(self, plugin_: plugin_base.Plugin, context: dict) -> str:
        return ""

    def render(self, context) -> str:
        plugin_ = self._get_plugin(context)
        context = self._get_context(context)
        return self._render(plugin_, context)


class RenderNavigationPlugin(_RenderPlugin):
    def _render(self, plugin_: plugin_base.Plugin, context: dict) -> str:
        try:
            return plugin_.render_navigation(context=context, render_location=self.render_location)
        except Exception:
            # Use a broad exception to prevent a template error in a plugin from breaking Tanzawa
            logger.exception("Error rendering %s, %s", plugin_, self.render_location)
            return ""


@register.tag(name="render_navigation")
def do_render_navigation(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, plugin_identifier, render_location = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a plugin identifier and location  arguments" % token.contents.split()[0]
        )
    return RenderNavigationPlugin(plugin=template.Variable(plugin_identifier), render_location=render_location)


@register.tag(name="render_after_content")
def do_render_after_content(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, plugin_identifier, render_location = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a plugin identifier and location  arguments" % token.contents.split()[0]
        )
    return RenderNavigationPlugin(plugin=template.Variable(plugin_identifier), render_location=render_location)
