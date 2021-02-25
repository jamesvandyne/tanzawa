from typing import List, Optional

from bs4 import BeautifulSoup
from django import forms
from django.db import transaction
from django.utils.timezone import now
from files.models import TFile
from files.utils import extract_uuid_from_url
from indieweb.constants import MPostKinds, MPostStatuses
from post.models import MPostKind, MPostStatus, TPost
from trix.forms import TrixField
from trix.utils import extract_attachment_urls
from streams.models import MStream
from streams.forms import StreamModelMultipleChoiceField

from .models import TEntry


class TCharField(forms.CharField):
    widget = forms.TextInput(attrs={"class": "input-field"})


class CreateStatusForm(forms.ModelForm):
    p_name = TCharField(required=False, label="Title")
    e_content = TrixField(required=True)
    m_post_status = forms.ModelChoiceField(
        MPostStatus.objects.all(),
        to_field_name="key",
        required=True,
        empty_label=None,
        initial=MPostStatuses.draft,
    )
    streams = StreamModelMultipleChoiceField(
        MStream.objects.all(),
        label="Which streams should this appear in?",
        required=False,
    )

    m_post_kind = MPostKinds.note

    class Meta:
        model = TEntry
        fields = ("p_name", "e_content")

    def __init__(self, *args, **kwargs):
        self.p_author = kwargs.pop("p_author")
        autofocus = kwargs.pop("autofocus", "e_content")
        super().__init__(*args, **kwargs)
        self.fields["m_post_status"].widget.attrs = {
            "class": "mb-1",
        }
        self.fields["p_name"].widget.attrs.update({"placeholder": "Title"})

        if autofocus:
            self.fields[autofocus].widget.attrs.update({"autofocus": "autofocus"})

        self.t_post: Optional[TPost] = None
        self.t_entry: Optional[TEntry] = None
        self.file_attachment_uuids: List[str] = []

    def clean(self):
        try:
            self.cleaned_data["m_post_kind"] = MPostKind.objects.get(
                key=self.m_post_kind
            )
        except MPostKind.DoesNotExist:
            raise forms.ValidationError(
                f"m_post_kind: {self.m_post_kind} does not exist"
            )

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
        soup = BeautifulSoup(self.cleaned_data["e_content"], "html.parser")
        self.instance = TEntry(
            e_content=self.cleaned_data["e_content"],
            p_summary=soup.text[:255].strip(),
            p_name=self.cleaned_data.get("p_name", ""),
        )

    @transaction.atomic
    def save(self, commit=True):
        self.t_post.save()
        self.instance.t_post = self.t_post
        entry = super().save(commit)
        self.t_post.files.set(TFile.objects.filter(uuid__in=self.file_attachment_uuids))
        self.t_post.streams.set(self.cleaned_data["streams"])
        return entry


class CreateArticleForm(CreateStatusForm):
    m_post_kind = MPostKinds.article

    class Meta:
        model = TEntry
        fields = ("p_name", "e_content")


class CreateReplyForm(CreateStatusForm):
    m_post_kind = MPostKinds.reply

    u_in_reply_to = forms.URLField(label="What's the URL you're replying to?", widget=forms.HiddenInput)
    author = forms.CharField(label='Author', widget=forms.HiddenInput)
    title = forms.CharField(label='Title')
    summary = forms.CharField(widget=forms.Textarea, label='Summary',
                              help_text='This will appear above your reply as a quote for context.')

    class Meta:
        model = TEntry
        fields = ("p_name", "e_content")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["summary"].widget.attrs = {"class": "input-field"}
        self.fields["e_content"].label = "My Response"


class ExtractMetaForm(forms.Form):
    url = forms.URLField(required=True, label="What's the URL you're replying to?")

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance", None)
        kwargs.pop("p_author", None)
        kwargs.pop("autofocus", None)
        super().__init__(*args, **kwargs)
        self.fields["url"].widget.attrs = {
            "data-url-submit-target": "field",
            "data-action": "url-submit#input",
            "autofocus": "autofocus",
            "class": "input-field",
            "placeholder": "https://tanzawa.blog",
        }


class UpdateStatusForm(forms.ModelForm):
    p_name = TCharField(required=False, label="Title")
    e_content = TrixField(required=True)
    m_post_status = forms.ModelChoiceField(
        MPostStatus.objects.all(),
        to_field_name="key",
        required=True,
        empty_label=None,
        initial=MPostStatuses.draft,
    )
    streams = StreamModelMultipleChoiceField(
        MStream.objects.all(),
        label="Which streams should this appear in?",
        required=False,
    )

    class Meta:
        model = TEntry
        fields = ("e_content",)

    def __init__(self, *args, **kwargs):
        autofocus = kwargs.pop("autofocus", "e_content")
        super().__init__(*args, **kwargs)
        self.t_post: TPost = self.instance.t_post
        self.already_published = (
            self.t_post.m_post_status.key == MPostStatuses.published
        )
        self.fields["streams"].initial = self.t_post.streams.values_list(
            "id", flat=True
        )
        self.fields["p_name"].widget.attrs.update({"placeholder": "Title"})

        if autofocus:
            self.fields[autofocus].widget.attrs.update({"autofocus": "autofocus"})
        self.file_attachment_uuids: List[str] = []

    def clean(self):
        urls = extract_attachment_urls(self.cleaned_data["e_content"])
        self.file_attachment_uuids = [extract_uuid_from_url(url) for url in urls]

    def prepare_data(self):
        n = now()
        self.t_post.m_post_status = self.cleaned_data["m_post_status"]
        if self.t_post.m_post_status.key == MPostStatuses.published:
            if not self.already_published:
                self.t_post.dt_published = n
        else:  # draft
            self.t_post.dt_published = None
        self.t_post.dt_updated = n
        soup = BeautifulSoup(self.cleaned_data["e_content"], features="html5lib")
        self.instance.p_summary = soup.text[:255]

    @transaction.atomic
    def save(self, commit: bool = True):
        super().save(commit=commit)
        self.t_post.save()
        self.t_post.files.set(TFile.objects.filter(uuid__in=self.file_attachment_uuids))
        self.t_post.streams.set(self.cleaned_data["streams"])
        return self.instance


class UpdateArticleForm(UpdateStatusForm):
    class Meta:
        model = TEntry
        fields = ("p_name", "e_content")
