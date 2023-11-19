from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def abs_url(context, view_name, *args, **kwargs):
    return context["request"].build_absolute_uri(reverse(view_name, args=args, kwargs=kwargs))


@register.filter
def as_abs_url(path, request):
    return request.build_absolute_uri(path)
