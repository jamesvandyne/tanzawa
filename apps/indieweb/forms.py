from django import forms
from django.db import transaction
from rest_framework.authtoken.models import Token

from .models import MMicropubScope, TToken, TTokenMicropubScope


class MMicropubCheckboxWidget(forms.CheckboxSelectMultiple):

    option_template_name = "micropub_checkbox_option.html"


class IndieAuthAuthorizationForm(forms.Form):

    client_id = forms.URLField(widget=forms.HiddenInput)
    redirect_uri = forms.URLField(widget=forms.HiddenInput)
    state = forms.CharField(widget=forms.HiddenInput)
    scope = forms.ModelMultipleChoiceField(
        MMicropubScope.objects,
        to_field_name="key",
        required=True,
        widget=MMicropubCheckboxWidget,
    )

    @transaction.atomic
    def save(self, user) -> TToken:
        token = Token.objects.create(user=user)
        t_token = TToken.objects.create(
            client_id=self.cleaned_data["client_id"], token=token
        )
        t_token.micropub_scope.set(self.cleaned_data["scope"])
        return t_token
