from typing import Optional
import uuid
from django import forms
from django.contrib.gis.geos import Point

from .models import TFile
from .exif import get_location


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = TFile
        fields = ["file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.point: Optional[Point] = None

    def clean(self):
        self.instance.uuid = uuid.uuid4()
        self.instance.point = get_location(self.cleaned_data['file'])
