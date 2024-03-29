from django import forms
from django.template.loader import render_to_string


class TrixEditor(forms.Textarea):
    editor_template = "trix/editor.html"

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs.update({"style": "visibility: hidden; position: absolute;"})

        params = {
            "input": attrs.get("id") or f"{name}_id",
            "class": "trix-content",
        }
        param_str = " ".join(f'{k}="{v}"' for k, v in params.items())

        html = super().render(name, value, attrs)
        context = {"html": html, "param_str": param_str}
        html = render_to_string(self.editor_template, context=context)
        return html

    class Media:
        css = {"all": ("trix/trix.css",)}


class MinimalTrixEditor(TrixEditor):
    editor_template = "trix/minimal_editor.html"
