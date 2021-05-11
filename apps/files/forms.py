import uuid
from typing import Optional

import plum
from django import forms
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile

from .images import rotate_image
from .exif import extract_exif, get_location, scrub_exif
from .models import TFile


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = TFile
        fields = ["file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.point: Optional[Point] = None

    def clean(self):
        self.instance.uuid = uuid.uuid4()
        self.instance.mime_type = self.files["file"].content_type
        try:
            exif = extract_exif(self.cleaned_data["file"].file)

            self.instance.exif = exif
            self.instance.point = get_location(exif)
            self.cleaned_data["file"].seek(0)

            rotated_image = rotate_image(
                self.cleaned_data["file"].file, self.cleaned_data["file"].content_type
            )
            scrubbed_image_data = scrub_exif(rotated_image)
            image_data = scrubbed_image_data if scrubbed_image_data else rotated_image
            image_data.seek(0)
            upload_file = SimpleUploadedFile(
                self.cleaned_data["file"].name,
                image_data.read(),
                self.cleaned_data["file"].content_type,
            )
            self.cleaned_data["file"] = upload_file
        except plum._exceptions.UnpackError:
            pass
