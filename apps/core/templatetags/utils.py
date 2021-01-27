from typing import Dict, Optional, Any
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
