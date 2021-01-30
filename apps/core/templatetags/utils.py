import mimetypes
from typing import Any, Dict, Optional
from urllib import parse

import ftfy
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


@register.filter
def mimetype(obj: str) -> str:
    if obj is None:
        return ""
    return mimetypes.guess_type(obj)[0]


@register.filter
def fix_text(obj: str) -> str:
    if not obj:
        return ""
    return ftfy.fix_text(ftfy.fixes.decode_escapes(obj))
