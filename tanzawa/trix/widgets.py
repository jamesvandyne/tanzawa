from __future__ import unicode_literals

from django import forms
from django.template.loader import render_to_string


class TrixEditor(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs.update({"style": "visibility: hidden; position: absolute;"})

        params = {
            "input": attrs.get("id") or "{}_id".format(name),
            "class": "trix-content",
        }
        param_str = " ".join('{}="{}"'.format(k, v) for k, v in params.items())

        html = super(TrixEditor, self).render(name, value, attrs)
        context = {"html": html, "param_str": param_str}
        html = render_to_string("trix/editor.html", context=context)
        return html

    class Media:
        css = {"all": ("trix/trix.css",)}
