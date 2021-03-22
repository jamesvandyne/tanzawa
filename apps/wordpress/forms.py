from django import forms

from .models import TWordpress


class WordpressUploadForm(forms.ModelForm):
    class Meta:
        model = TWordpress
        fields = ["export_file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_export_file(self):
        if self.cleaned_data["export_file"].content_type not in [
            "application/xml",
            "text/xml",
        ]:
            raise forms.ValidationError("File must be XML")
        return self.cleaned_data["export_file"]

    def clean(self):
        # Extract basic link / base url and so forth information
        # prepare base transaction records for the import
        pass
