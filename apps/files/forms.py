from django import forms

from .models import TFile


class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = TFile
        fields = ["file"]
