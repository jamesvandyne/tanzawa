from django import forms
from.models import MMicropubScope


class MMicropubCheckboxWidget(forms.CheckboxSelectMultiple):

    option_template_name = "micropub_checkbox_option.html"


class IndieAuthAuthorizationForm(forms.Form):

    scope = forms.ModelMultipleChoiceField(MMicropubScope.objects,
                                           to_field_name='key',
                                           required=True,
                                           widget=MMicropubCheckboxWidget)
