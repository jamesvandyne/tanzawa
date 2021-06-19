from django import forms


class TCharField(forms.CharField):
    widget = forms.TextInput(attrs={"class": "input-field"})