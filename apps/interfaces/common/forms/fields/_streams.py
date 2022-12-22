from django import forms

from data.streams.models import MStream


class _StreamCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    option_template_name = "streams/fragments/stream_checkbox_option.html"


class StreamModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    widget = _StreamCheckboxSelectMultiple(attrs={"class": "inline-flex flex-wrap"})

    def label_from_instance(self, obj: MStream) -> str:
        return f"{obj.icon} {obj.name}"


class StreamModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: MStream) -> str:
        return f"{obj.icon} {obj.name}"
