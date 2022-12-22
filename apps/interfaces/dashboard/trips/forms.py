from django import forms
from django.contrib.gis.forms import PointField
from django.utils.timezone import now

from core.constants import VISIBILITY_CHOICES, Visibility
from core.forms import LeafletWidget, TCharField, TDateField, TTextArea
from data.trips.models import TTrip, TTripLocation


class TTripModelForm(forms.ModelForm):
    class Meta:
        model = TTrip
        fields = (
            "name",
            "d_start",
            "d_end",
            "p_summary",
            "visibility",
        )

    name = TCharField(label="Name?")
    d_start = TDateField(required=False, label="Start", initial=now)
    d_end = TDateField(required=False, label="End")
    p_summary = TTextArea(
        required=False,
        label="Why did you go?",
        help_text="A brief summary to provide context for your trip. Optional, but recommended.",
    )
    visibility = forms.ChoiceField(
        choices=VISIBILITY_CHOICES, initial=Visibility.PUBLIC.value, label="Who should see this post?"
    )

    def __init__(self, *args, **kwargs):
        self.p_author = kwargs.pop("p_author", None)
        super().__init__(*args, **kwargs)
        self.fields["p_summary"].widget.attrs["rows"] = "3"
        select_attrs = {
            "class": "mb-1 w-52",
            "form": "trip",
        }
        self.fields["visibility"].widget.attrs = select_attrs
        self.fields["visibility"].initial = Visibility.PUBLIC

    def clean(self):
        super().clean()
        if self.p_author:
            self.instance.p_author = self.p_author


class TLocationModelForm(forms.ModelForm):
    point = PointField(widget=LeafletWidget, required=False, label="Where did you start?")

    class Meta:
        model = TTripLocation
        exclude = ("created_at", "updated_at", "t_trip")
        widgets = {
            "street_address": forms.HiddenInput({"data-leaflet-target": "streetAddress"}),
            "locality": forms.HiddenInput({"data-leaflet-target": "locality"}),
            "region": forms.HiddenInput({"data-leaflet-target": "region"}),
            "country_name": forms.HiddenInput({"data-leaflet-target": "country"}),
            "postal_code": forms.HiddenInput({"data-leaflet-target": "postalCode"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def prepare_data(self, t_trip: TTrip):
        self.instance.t_trip = t_trip

    def save(self, commit=True):
        if self.cleaned_data["point"]:
            super().save(commit=commit)
        elif self.instance.pk:
            self.instance.delete()
        return self.instance
