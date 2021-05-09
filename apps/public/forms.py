from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "What are you looking for?", "class": "input-field"}
        ),
    )
    lat = forms.FloatField(required=False)
    lon = forms.FloatField(required=False)
    m = forms.BooleanField(required=False, label="Show map")

    def clean(self):
        if (
            self.cleaned_data.get("lat")
            and not self.cleaned_data.get("lon")
            or self.cleaned_data.get("lon")
            and not self.cleaned_data.get("lat")
        ):
            raise forms.ValidationError(
                "Both lat and lon are required for geo searches"
            )
