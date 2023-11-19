from django import forms
from taggit import forms as taggit_forms


class BookmarksSearchForm(forms.Form):
    tag = taggit_forms.TagField(required=False)
