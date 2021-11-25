from django import forms as django_forms
from trix import forms as trix_forms


class UpdateNow(django_forms.Form):
    content = trix_forms.TrixField(required=False, label="What are you focusing on now?")
