from typing import List
from django import forms
from django.db import transaction
from bs4 import BeautifulSoup

from .models import TWordpress, TCategory


class WordpressUploadForm(forms.ModelForm):
    class Meta:
        model = TWordpress
        fields = ["export_file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t_categories: List[TCategory] = []

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

    def _extract_categories(self, soup):
        categories = set(soup.find_all('category', attrs={"domain": "category"}))
        self.t_categories.extend([TCategory(
            name=category.text,
            nice_name=category.attrs['nicename']) for category in categories])

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save(commit)

        for t_category in self.t_categories:
            t_category.t_wordpress = instance
        TCategory.objects.bulk_create(self.t_categories)



        return instance