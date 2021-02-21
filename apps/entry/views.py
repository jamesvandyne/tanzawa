from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import mark_safe
from django.views.generic import ListView, CreateView, UpdateView
from indieweb.constants import MPostStatuses, MPostKinds
from indieweb.webmentions import send_webmention
from post.models import MPostKind

from . import forms, models


@method_decorator(login_required, name="dispatch")
class CreateEntryView(CreateView):
    autofocus = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"p_author": self.request.user, "autofocus": self.autofocus})
        return kwargs

    def form_valid(self, form):
        form.prepare_data()
        entry = form.save()

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            send_webmention(self.request, entry.t_post, entry.e_content)

        permalink_a_tag = render_to_string(
            "fragments/view_post_link.html", {"t_post": entry.t_post}
        )
        messages.success(
            self.request,
            f"Saved {form.cleaned_data['m_post_kind']}. {mark_safe(permalink_a_tag)}",
        )
        return redirect(resolve_url("status_edit", pk=entry.pk))

    def form_invalid(self, form):
        context = {"form": form, "nav": "status"}
        return render(self.request, self.template_name, context=context)


@method_decorator(login_required, name="dispatch")
class UpdateEntryView(UpdateView):
    m_post_kind = None
    original_content = ""

    def get_queryset(self):
        return models.TEntry.objects.select_related("t_post").filter(
            t_post__m_post_kind__key=self.m_post_kind
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        self.original_content = obj.e_content
        return obj

    def form_valid(self, form):
        form.prepare_data()
        send_webmention(self.request, form.instance.t_post, self.original_content)
        form.save()
        send_webmention(self.request, form.instance.t_post, form.instance.e_content)
        permalink_a_tag = render_to_string(
            "fragments/view_post_link.html", {"t_post": form.instance.t_post}
        )
        messages.success(
            self.request,
            f"Saved {form.instance.t_post.m_post_kind.key}. {mark_safe(permalink_a_tag)}",
        )
        context = {"form": form, "nav": "status"}
        return render(self.request, self.template_name, context=context)

    def form_invalid(self, form):
        context = {"form": form, "nav": "status"}
        return render(self.request, self.template_name, context=context)


# Note CRUD views


class CreateStatusView(CreateEntryView):
    form_class = forms.CreateStatusForm
    template_name = "entry/note/create.html"


class UpdateStatusView(UpdateEntryView):
    form_class = forms.UpdateStatusForm
    template_name = "entry/note/update.html"
    m_post_kind = MPostKinds.note


# Article CRUD views


class CreateArticleView(CreateEntryView):
    form_class = forms.CreateArticleForm
    template_name = "entry/article/create.html"
    autofocus = "p_name"


class UpdateArticleView(UpdateEntryView):
    form_class = forms.UpdateArticleForm
    template_name = "entry/article/update.html"
    m_post_kind = MPostKinds.article
    autofocus = "p_name"


@login_required
def status_detail(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related("t_post"), pk=pk)
    context = {"status": status, "nav": "status"}
    return render(request, "entry/status_detail.html", context=context)


@login_required
def status_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects, pk=pk)
    send_webmention(request, status.t_post, status.e_content)
    status.delete()
    # TODO: Should we also delete the t_post ?
    messages.success(request, "Status Deleted")
    return redirect(resolve_url("status_list"))


@method_decorator(login_required, name="dispatch")
class TEntryListView(ListView):
    template_name = "entry/status_list.html"
    m_post_kind_key = None
    m_post_kind = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.m_post_kind_key:
            self.m_post_kind = get_object_or_404(MPostKind, key=self.m_post_kind_key)

    def get_queryset(self):
        qs = models.TEntry.objects.all()
        if self.m_post_kind:
            qs = qs.filter(t_post__m_post_kind=self.m_post_kind)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["nav"] = "status"
        return context


@login_required
def article_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects, pk=pk)
    send_webmention(request, status.t_post, status.e_content)
    status.delete()
    # TODO: Should we also delete the t_post ?
    messages.success(request, "Article Deleted")
    return redirect(resolve_url("status_list"))
