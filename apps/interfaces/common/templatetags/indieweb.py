from django import template

register = template.Library()


class RenderRelme(template.Node):
    def render(self, context):
        from domain.indieweb.relme import queries as relme_queries

        t = context.template.engine.get_template("indieweb/relme/header.html")
        return t.render(context=template.Context({"all_relme": relme_queries.get_relme()}))


@register.tag(name="render_relme")
def do_render_relme(parser, token):

    return RenderRelme()
