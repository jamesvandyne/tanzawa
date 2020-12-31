from typing import Optional

from django import forms
from django.db import transaction
from trix.widgets import TrixEditor

from post.models import MPostStatus, MPostKind, TPost
from indieweb.constants import MPostKinds, MPostStatuses

from .models import TEntry


class CreateArticleForm(forms.Form):
    p_name = forms.CharField(required=True)
    e_content = forms.CharField(required=True, widget=TrixEditor)
    m_post_status = forms.ModelChoiceField(MPostStatus.objects.all(), to_field_name="key", required=True, empty_label=None, initial=MPostStatuses.draft)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["p_name"].widget.attrs = {
            'class': 'block w-full border border-gray-400 p-1 mb-2  rounded-sm',
        }
        self.fields["m_post_status"].widget.attrs = {
            'class': 'mb-1',
        }
        self.t_post: Optional[TPost] = None
        self.t_entry: Optional[TEntry] = None

    def clean(self):
        try:
            self.cleaned_data['m_post_kind'] = MPostKind.objects.get(key=MPostKinds.article)
        except MPostKind.DoesNotExist:
            raise forms.ValidationError("m_post_kind: article does not exist")

    def prepare_data(self):
        self.t_post = TPost(m_post_status=self.cleaned_data["m_post_status"],
                            m_post_kind=self.cleaned_data["m_post_kind"])
        self.t_entry = TEntry(p_name=self.cleaned_data['p_name'],
                              e_content=self.cleaned_data['e_content'])

    @transaction.atomic
    def save(self):
        self.t_post.save()
        self.t_entry.t_post = self.t_post
        self.t_entry.save()
        return self.t_entry
