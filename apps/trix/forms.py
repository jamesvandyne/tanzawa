from bs4 import BeautifulSoup
from django import forms
from django.template.loader import render_to_string
from files.constants import PICTURE_FORMATS

from .widgets import TrixEditor


class TrixField(forms.CharField):
    widget = TrixEditor

    def to_python(self, value: str):
        value = super().to_python(value)

        soup = BeautifulSoup(value, "html.parser")

        figures = soup.select("figure[data-trix-content-type^=image]")
        # rewrite the image figures to use the picture tag and provide alternative / optimised urls
        for figure in figures:
            if figure.find("picture"):
                # already has a picture, so let's not rewrite it
                pass

            img = figure.find("img")
            if not img:
                pass
            context = {
                "source_formats": PICTURE_FORMATS.get(figure["data-trix-content-type"], []),
                "src": img["src"],
                "width": img["width"],
                "height": img["height"],
            }
            picture = BeautifulSoup(render_to_string("trix/picture.html", context), "html.parser")
            img.insert_before(picture)
            img.decompose()
        return str(soup)
