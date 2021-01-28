from typing import Any, Dict, Optional
from urllib import parse

from django import template

register = template.Library()


@register.filter
def get_key(obj: Optional[Dict[str, Any]] = None, key: str = "") -> str:
    if not obj:
        return ""
    try:
        return obj.get(key, "")
    except AttributeError:
        return ""


@register.filter
def domain(obj: str) -> str:
    if not obj:
        return ""
    return parse.urlparse(obj).netloc
