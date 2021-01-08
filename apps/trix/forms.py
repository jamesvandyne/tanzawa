from bs4 import BeautifulSoup
from django import forms

from .widgets import TrixEditor


class TrixField(forms.CharField):
    widget = TrixEditor

    def to_python(self, value):
        value: str = super().to_python(value)

        soup = BeautifulSoup(value, "html.parser")
        for img_tag in soup.find_all("img"):
            img_tag["loading"] = "lazy"
        return str(soup)
