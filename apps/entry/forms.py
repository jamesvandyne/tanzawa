from typing import List, Optional

from django import forms
from django.db import transaction
from django.utils.timezone import now
from files.models import TFile
from files.utils import extract_uuid_from_url
from indieweb.constants import MPostKinds, MPostStatuses
from post.models import MPostKind, MPostStatus, TPost
from trix.forms import TrixField
from trix.utils import extract_attachment_urls

from .models import TEntry


class CreateStatusForm(forms.Form):
    e_content = TrixField(required=True)
    m_post_status = forms.ModelChoiceField(
        MPostStatus.objects.all(),
        to_field_name="key",
        required=True,
        empty_label=None,
        initial=MPostStatuses.draft,
    )

    def __init__(self, *args, **kwargs):
        self.p_author = kwargs.pop("p_author")
        super().__init__(*args, **kwargs)
        self.fields["m_post_status"].widget.attrs = {
            "class": "mb-1",
        }
        self.t_post: Optional[TPost] = None
        self.t_entry: Optional[TEntry] = None
        self.file_attachment_uuids: List[str] = []

    def clean(self):
        try:
            self.cleaned_data["m_post_kind"] = MPostKind.objects.get(
                key=MPostKinds.note
            )
        except MPostKind.DoesNotExist:
            raise forms.ValidationError("m_post_kind: note does not exist")

        urls = extract_attachment_urls(self.cleaned_data["e_content"])
        self.file_attachment_uuids = [extract_uuid_from_url(url) for url in urls]

    def prepare_data(self):
        n = now()
        self.t_post = TPost(
            m_post_status=self.cleaned_data["m_post_status"],
            m_post_kind=self.cleaned_data["m_post_kind"],
            p_author=self.p_author,
            dt_published=n
            if self.cleaned_data["m_post_status"].key == MPostStatuses.published
            else None,
            dt_updated=n,
        )
        self.t_entry = TEntry(e_content=self.cleaned_data["e_content"])

    @transaction.atomic
    def save(self):
        self.t_post.save()
        self.t_entry.t_post = self.t_post
        self.t_entry.save()
        self.t_post.files.set(TFile.objects.filter(uuid__in=self.file_attachment_uuids))
        return self.t_entry


class UpdateStatusForm(forms.ModelForm):
    e_content = TrixField(required=True)
    m_post_status = forms.ModelChoiceField(
        MPostStatus.objects.all(),
        to_field_name="key",
        required=True,
        empty_label=None,
        initial=MPostStatuses.draft,
    )

    class Meta:
        model = TEntry
        fields = ("e_content",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t_post: TPost = self.instance.t_post
        self.already_published = (
            self.t_post.m_post_status.key == MPostStatuses.published
        )
        self.file_attachment_uuids: List[str] = []

    def clean(self):
        urls = extract_attachment_urls(self.cleaned_data["e_content"])
        self.file_attachment_uuids = [extract_uuid_from_url(url) for url in urls]

    def prepare_data(self):
        n = now()
        self.t_post.m_post_status = self.cleaned_data["m_post_status"]
        if (
            self.t_post.m_post_status.key == MPostStatuses.published
            and not self.already_published
        ):
            self.t_post.dt_published = n
        self.t_post.dt_updated = n

    @transaction.atomic
    def save(self, commit: bool = True):
        super().save(commit=commit)
        self.t_post.save()
        self.t_post.files.set(TFile.objects.filter(uuid__in=self.file_attachment_uuids))
        return self.instance
