from typing import List
from urllib.parse import urlparse
from django import forms
from django.db import transaction
from bs4 import BeautifulSoup

from post.models import TPost

from .models import (
    TWordpress,
    TCategory,
    TPostFormat,
    TPostKind,
    TWordpressAttachment,
    TWordpressPost,
)
from .extract import extract_categories, extract_post_kind, extract_post_format

from streams.models import MStream
from streams.forms import StreamModelChoiceField


class WordpressUploadForm(forms.ModelForm):
    class Meta:
        model = TWordpress
        fields = ["export_file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t_categories: List[TCategory] = []
        self.t_post_formats: List[TPostFormat] = []
        self.t_post_kinds: List[TPostKind] = []
        self.t_attachments: List[TWordpressAttachment] = []
        self.t_posts: List[TWordpressPost] = []

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

        self.t_categories.extend(
            [
                TCategory(name=name, nice_name=nice_name)
                for name, nice_name in extract_categories(soup)
            ]
        )
        self.t_post_formats.extend(
            [
                TPostFormat(name=name, nice_name=nice_name)
                for name, nice_name in extract_post_format(soup)
            ]
        )
        self.t_post_kinds.extend(
            [
                TPostKind(name=name, nice_name=nice_name)
                for name, nice_name in extract_post_kind(soup)
            ]
        )
        self._extract_attachments(soup)
        self._extract_posts(soup)

    def _extract_attachments(self, soup):
        attachments = soup.find_all("wp:post_type", text="attachment")
        self.t_attachments.extend(
            [
                TWordpressAttachment(
                    guid=attachment.parent.find("guid").text,
                    link=attachment.parent.find("link").text,
                )
                for attachment in attachments
            ]
        )

    def _extract_posts(self, soup):
        posts = soup.find_all("wp:post_type", text="post")
        self.t_posts.extend(
            [
                TWordpressPost(
                    guid=post.parent.find("guid").text,
                    path=urlparse(post.parent.find("link").text).path,
                )
                for post in posts
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

        for t_attachment in self.t_attachments:
            t_attachment.t_wordpress = instance
        TWordpressAttachment.objects.bulk_create(self.t_attachments)

        for t_post in self.t_posts:
            t_post.t_wordpress = instance
        TWordpressPost.objects.bulk_create(self.t_posts)

        return instance


class TCategoryModelForm(forms.ModelForm):

    t_stream = StreamModelChoiceField(
        MStream.objects, label="", empty_label="Skip", required=False
    )

    class Meta:
        model = TCategory
        fields = ("m_stream",)


class TPostKindModelForm(forms.ModelForm):
    class Meta:
        model = TPostKind
        fields = ("m_post_kind",)


class ImportTWordpressPostForm(forms.ModelForm):
    class Meta:
        model = TWordpressPost
        fields = ("t_post",)

    def __init__(self, *args, soup: BeautifulSoup, **kwargs):
        super().__init__(*args, **kwargs)
        self.soup = soup
        self.item = None

    def prepare_data(self):
        self.t_post = self.instance.t_post or TPost()

        # loop through item xml and prepare objects
