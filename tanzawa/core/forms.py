from django import forms
from django.contrib.gis.forms import OSMWidget


class TCharField(forms.CharField):
    widget = forms.TextInput(attrs={"class": "input-field"})


class TTextArea(forms.CharField):
    widget = forms.Textarea(attrs={"class": "input-field"})


class DateWidget(forms.DateInput):
    input_type = "date"


class TDateField(forms.DateField):
    widget = DateWidget


class LeafletWidget(OSMWidget):
    template_name = "gis/leaflet.html"
    default_zoom = 5
    default_lat = 35.45416667
    default_lon = 139.16333333
