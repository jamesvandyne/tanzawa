from typing import Optional

from django import forms
from django.db import transaction
from trix.widgets import TrixEditor

from post.models import MPostStatus, MPostKind, TPost
from indieweb.constants import MPostKinds, MPostStatuses

from .models import TEntry


class CreateStatusForm(forms.Form):
    e_content = forms.CharField(required=True, widget=TrixEditor)
    m_post_status = forms.ModelChoiceField(MPostStatus.objects.all(), to_field_name="key", required=True, empty_label=None, initial=MPostStatuses.draft)

    def __init__(self, *args, **kwargs):
        self.p_author = kwargs.pop("p_author")
        super().__init__(*args, **kwargs)
        self.fields["m_post_status"].widget.attrs = {
            'class': 'mb-1',
        }
        self.t_post: Optional[TPost] = None
        self.t_entry: Optional[TEntry] = None

    def clean(self):
        try:
            self.cleaned_data['m_post_kind'] = MPostKind.objects.get(key=MPostKinds.note)
        except MPostKind.DoesNotExist:
            raise forms.ValidationError("m_post_kind: note does not exist")

    def prepare_data(self):
        self.t_post = TPost(m_post_status=self.cleaned_data["m_post_status"],
                            m_post_kind=self.cleaned_data["m_post_kind"],
                            p_author=self.p_author)
        self.t_entry = TEntry(e_content=self.cleaned_data['e_content'])

    @transaction.atomic
    def save(self):
        self.t_post.save()
        self.t_entry.t_post = self.t_post
        self.t_entry.save()
        return self.t_entry


class UpdateStatusForm(forms.ModelForm):
    e_content = forms.CharField(required=True, widget=TrixEditor)
    m_post_status = forms.ModelChoiceField(MPostStatus.objects.all(), to_field_name="key", required=True, empty_label=None, initial=MPostStatuses.draft)

    class Meta:
        model = TEntry
        fields = ('e_content', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.t_post: TPost = self.instance.t_post

    def prepare_data(self):
        self.t_post.m_post_status = self.cleaned_data["m_post_status"]

    @transaction.atomic
    def save(self, commit: bool = True):
        super().save(commit=commit)
        self.t_post.save()
        return self.instance
