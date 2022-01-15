from django import template
from indieweb.domain.relme import queries as relme_queries

register = template.Library()


class RenderRelme(template.Node):
    def render(self, context):
        t = context.template.engine.get_template("indieweb/relme/header.html")
        return t.render(context=template.Context({"all_relme": relme_queries.get_relme()}))


@register.tag(name="render_relme")
def do_render_relme(parser, token):

    return RenderRelme()
