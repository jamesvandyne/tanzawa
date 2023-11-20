from django import template

from domain.indieweb import queries

register = template.Library()


class RenderRelme(template.Node):
    def render(self, context):
        from domain.indieweb.relme import queries as relme_queries

        t = context.template.engine.get_template("indieweb/relme/header.html")
        return t.render(context=template.Context({"all_relme": relme_queries.get_relme()}))


@register.tag(name="render_relme")
def do_render_relme(parser, token):
    return RenderRelme()


@register.filter(name="webmention_emojis")
def get_webmention_emojis(comment_types: list[str]) -> str:
    emojis = [queries.emoji_for_kind(kind) for kind in comment_types]
    return "".join([emoji for emoji in emojis if emoji])
