from typing import List, Optional

from bs4 import BeautifulSoup
from django import forms
from django.db import transaction
from django.contrib.gis.forms import OSMWidget, PointField
from django.utils.timezone import now
from files.models import TFile
from files.utils import extract_uuid_from_url
from indieweb.constants import MPostKinds, MPostStatuses
from post.models import MPostKind, MPostStatus, TPost
from trix.forms import TrixField
from trix.utils import extract_attachment_urls
from streams.models import MStream
from streams.forms import StreamModelMultipleChoiceField

from .models import TEntry, TReply, TBookmark, TLocation


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
    def save(self, commit=True) -> TEntry:
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

    u_in_reply_to = forms.URLField(
        label="What's the URL you're replying to?", widget=forms.HiddenInput
    )
    author = forms.CharField(label="Author", widget=forms.HiddenInput, required=False)
    author_url = forms.URLField(widget=forms.HiddenInput, required=False)
    author_photo_url = forms.URLField(widget=forms.HiddenInput, required=False)
    title = forms.CharField(label="Title", widget=forms.HiddenInput)
    summary = forms.CharField(
        widget=forms.Textarea,
        label="Summary",
        help_text="This will appear above your reply as a quote for context.",
    )

    class Meta:
        model = TEntry
        fields = ("p_name", "e_content")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["summary"].widget.attrs = {"class": "input-field"}
        self.fields["e_content"].label = "My Response"
        self.t_reply: Optional[TReply] = None
        for key, val in self.initial.items():
            if not val:
                self.fields[key].widget = forms.TextInput(
                    attrs={"class": "input-field"}
                )

    def prepare_data(self):
        super().prepare_data()
        self.t_reply = TReply(
            u_in_reply_to=self.cleaned_data["u_in_reply_to"],
            title=self.cleaned_data["title"],
            quote=self.cleaned_data["summary"],
            author=self.cleaned_data["author"],
            author_url=self.cleaned_data["author_url"],
            author_photo=self.cleaned_data["author_photo_url"],
        )

    def save(self, commit=True) -> TEntry:
        t_entry = super().save()
        if self.t_reply:
            self.t_reply.t_entry = t_entry
            self.t_reply.save()
        return t_entry


class ExtractMetaForm(forms.Form):
    url = forms.URLField(required=True, label="What's the URL you're replying to?")

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance", None)
        kwargs.pop("p_author", None)
        kwargs.pop("autofocus", None)
        label = kwargs.pop("label", None)
        super().__init__(*args, **kwargs)
        if label:
            self.fields["url"].label = label
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


class UpdateReplyForm(UpdateStatusForm):
    u_in_reply_to = forms.URLField(
        label="What's the URL you're replying to?", widget=forms.HiddenInput
    )
    title = forms.CharField(label="Title", widget=forms.HiddenInput)
    summary = forms.CharField(
        widget=forms.Textarea,
        label="Summary",
        help_text="This will appear above your reply as a quote for context.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["summary"].widget.attrs = {"class": "input-field"}
        self.fields["e_content"].label = "My Response"
        self.t_reply: TReply = self.instance.t_reply
        self.fields["summary"].initial = self.t_reply.quote
        self.fields["title"].initial = self.t_reply.title
        self.fields["u_in_reply_to"].initial = self.t_reply.u_in_reply_to

    def prepare_data(self):
        super().prepare_data()
        self.t_reply.quote = self.cleaned_data["summary"]

    def save(self, commit=True) -> TEntry:
        t_entry = super().save()
        self.t_reply.save()
        return t_entry


class CreateBookmarkForm(CreateStatusForm):
    m_post_kind = MPostKinds.bookmark

    u_bookmark_of = forms.URLField(
        label="What's the URL you're bookmarking?", widget=forms.HiddenInput
    )
    author = forms.CharField(label="Author", widget=forms.HiddenInput, required=False)
    author_url = forms.URLField(widget=forms.HiddenInput, required=False)
    author_photo_url = forms.URLField(widget=forms.HiddenInput, required=False)
    title = forms.CharField(label="Title", widget=forms.HiddenInput)
    summary = forms.CharField(
        widget=forms.Textarea,
        label="Quote (Optional)",
        help_text="This is will appear above your comment for context.",
        required=False,
    )

    class Meta:
        model = TEntry
        fields = ("p_name", "e_content")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["summary"].widget.attrs = {"class": "input-field"}
        self.fields["e_content"].label = "Comment"
        self.t_bookmark: Optional[TBookmark] = None
        for key, val in self.initial.items():
            if not val:
                self.fields[key].widget = forms.TextInput(
                    attrs={"class": "input-field"}
                )

    def prepare_data(self):
        super().prepare_data()
        self.t_bookmark = TBookmark(
            u_bookmark_of=self.cleaned_data["u_bookmark_of"],
            title=self.cleaned_data["title"],
            quote=self.cleaned_data["summary"],
            author=self.cleaned_data["author"],
            author_url=self.cleaned_data["author_url"],
            author_photo=self.cleaned_data["author_photo_url"],
        )

    def save(self, commit=True) -> TEntry:
        t_entry = super().save()
        if self.t_bookmark:
            self.t_bookmark.t_entry = t_entry
            self.t_bookmark.save()
        return t_entry


class UpdateBookmarkForm(UpdateStatusForm):
    u_bookmark_of = forms.URLField(
        label="What's the URL you're replying to?", widget=forms.HiddenInput
    )
    title = forms.CharField(label="Title", widget=forms.HiddenInput)
    summary = forms.CharField(
        widget=forms.Textarea,
        label="Quote (Optional)",
        help_text="This is will appear above your comment for context.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["summary"].widget.attrs = {"class": "input-field"}
        self.fields["e_content"].label = "My Response"
        self.t_bookmark: TBookmark = self.instance.t_bookmark
        self.fields["summary"].initial = self.t_bookmark.quote
        self.fields["title"].initial = self.t_bookmark.title
        self.fields["u_bookmark_of"].initial = self.t_bookmark.u_bookmark_of

    def prepare_data(self):
        super().prepare_data()
        self.t_bookmark.quote = self.cleaned_data["summary"]

    def save(self, commit=True) -> TEntry:
        t_entry = super().save()
        self.t_bookmark.save()
        return t_entry


class LeafletWidget(OSMWidget):
    template_name = "gis/leaflet.html"
    default_zoom = 5
    default_lat = 35.45416667
    default_lon = 139.16333333


class TLocationModelForm(forms.ModelForm):
    point = PointField(widget=LeafletWidget, required=False)

    class Meta:
        model = TLocation
        exclude = ("created_at", "updated_at", "t_entry")
        widgets = {
            "street_address": forms.HiddenInput(
                {"data-leaflet-target": "streetAddress"}
            ),
            "locality": forms.HiddenInput({"data-leaflet-target": "locality"}),
            "region": forms.HiddenInput({"data-leaflet-target": "region"}),
            "country_name": forms.HiddenInput({"data-leaflet-target": "country"}),
            "postal_code": forms.HiddenInput({"data-leaflet-target": "postalCode"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def prepare_data(self, t_entry: TEntry):
        self.instance.t_entry = t_entry

    def save(self, commit=True):
        if self.cleaned_data["point"]:
            super().save(commit=commit)
        elif self.instance.pk:
            # TLocation.point is non-nullable, so must be deleted if a user unsets the location
            self.instance.delete()
        return self.instance


TLocationFormSet = forms.modelformset_factory(
    TLocation, form=TLocationModelForm, min_num=1, max_num=1, extra=0
)
