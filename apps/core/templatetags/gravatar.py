from hashlib import md5
from urllib import parse

from django import template

register = template.Library()


def get_gravatar_url(email: str | None = None, size=40) -> str:
    if email is None:
        return ""
    digest = md5(email.lower().encode("utf-8")).hexdigest()
    # construct the url
    params = parse.urlencode({"d": "mm", "r": "g", "s": str(size)})
    return f"https://www.gravatar.com/avatar/{digest}?{params}"


@register.filter(name="gravatar_url")
def gravatar_url(email: str | None = None) -> str:
    return get_gravatar_url(email, 40)


@register.filter(name="retina_gravatar_url")
def retina_gravatar_url(email: str | None = None) -> str:
    retina = get_gravatar_url(email, 80)
    return f"{retina} 2x" if retina else retina
