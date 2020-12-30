from django import forms
from trix.widgets import TrixEditor


class CreateEntryForm(forms.Form):
    h = forms.CharField(widget=forms.HiddenInput)
    action = forms.CharField(widget=forms.HiddenInput)
    name = forms.CharField(required=True)
    content = forms.CharField(required=True, widget=TrixEditor)

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        initial.update({
            "h": "entry",
            "action": "create",
        })
        super().__init__(*args, initial=initial, **kwargs)
        self.fields["name"].widget.attrs = {
            'class': 'block w-full border border-gray-400 p-1 mb-2  rounded-sm',
        }
