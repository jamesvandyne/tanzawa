from django import forms

from data.indieweb.models import MMicropubScope


class MMicropubCheckboxWidget(forms.CheckboxSelectMultiple):

    option_template_name = "indieweb/fragments/micropub_checkbox_option.html"


class IndieAuthAuthorizationForm(forms.Form):

    client_id = forms.URLField(widget=forms.HiddenInput)
    redirect_uri = forms.URLField(widget=forms.HiddenInput)
    state = forms.CharField(widget=forms.HiddenInput)
    scope = forms.ModelMultipleChoiceField(
        MMicropubScope.objects,
        to_field_name="key",
        required=False,
        widget=MMicropubCheckboxWidget,
    )
