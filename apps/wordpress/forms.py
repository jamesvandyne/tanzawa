from typing import List
from django import forms
from django.db import transaction
from bs4 import BeautifulSoup

from .models import TWordpress, TCategory, TPostFormat, TPostKind


class WordpressUploadForm(forms.ModelForm):
    class Meta:
        model = TWordpress
        fields = ["export_file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t_categories: List[TCategory] = []
        self.t_post_formats: List[TPostFormat] = []
        self.t_post_kinds: List[TPostKind] = []

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
        soup = BeautifulSoup(self.cleaned_data["export_file"], "xml")
        self.instance.link = soup.find("link").text
        self.instance.base_site_url = soup.find("wp:base_site_url").text
        self.instance.base_blog_url = soup.find("wp:base_blog_url").text

        self._extract_categories(soup)
        self._extract_post_format(soup)
        self._extract_post_kind(soup)

    def _extract_categories(self, soup):
        categories = set(soup.find_all("category", attrs={"domain": "category"}))
        self.t_categories.extend(
            [
                TCategory(name=category.text, nice_name=category.attrs["nicename"])
                for category in categories
            ]
        )

    def _extract_post_kind(self, soup):
        categories = set(soup.find_all("category", attrs={"domain": "kind"}))
        self.t_post_kinds.extend(
            [
                TPostKind(name=category.text, nice_name=category.attrs["nicename"])
                for category in categories
            ]
        )

    def _extract_post_format(self, soup):
        categories = set(soup.find_all("category", attrs={"domain": "post_format"}))
        self.t_post_formats.extend(
            [
                TPostFormat(name=category.text, nice_name=category.attrs["nicename"])
                for category in categories
            ]
        )

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save(commit)

        for t_category in self.t_categories:
            t_category.t_wordpress = instance
        TCategory.objects.bulk_create(self.t_categories)

        for t_post_kind in self.t_post_kinds:
            t_post_kind.t_wordpress = instance
        TPostKind.objects.bulk_create(self.t_post_kinds)

        for t_post_format in self.t_post_formats:
            t_post_format.t_wordpress = instance
        TPostFormat.objects.bulk_create(self.t_post_formats)

        return instance
