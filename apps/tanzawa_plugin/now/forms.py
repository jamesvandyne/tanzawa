from django import forms as django_forms

from interfaces.common import forms as common_forms


class UpdateNow(django_forms.Form):
    content = common_forms.TrixField(required=False, label="What are you focusing on now?")
