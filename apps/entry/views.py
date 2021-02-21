from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import mark_safe
from django.views.generic import ListView, CreateView
from indieweb.constants import MPostStatuses
from indieweb.webmentions import send_webmention
from post.models import MPostKind

from . import forms, models


@method_decorator(login_required, name="dispatch")
class AuthorCreateEntryView(CreateView):
    autofocus = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'p_author': self.request.user,
            'autofocus': self.autofocus
        })
        return kwargs

    def form_valid(self, form):
        form.prepare_data()
        entry = form.save()

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            send_webmention(self.request, entry.t_post, entry.e_content)

        permalink_a_tag = render_to_string(
            "fragments/view_post_link.html", {"t_post": entry.t_post}
        )
        messages.success(self.request, f"Saved {form.cleaned_data['m_post_kind']}. {mark_safe(permalink_a_tag)}")
        return redirect(resolve_url("status_edit", pk=entry.pk))

    def form_invalid(self, form):
        context = {"form": form, "nav": "status"}
        return render(self.request, self.template_name, context=context)


class CreateStatusView(AuthorCreateEntryView):
    form_class = forms.CreateStatusForm
    template_name = "entry/status_create.html"


class CreateArticleView(AuthorCreateEntryView):
    form_class = forms.CreateArticleForm
    template_name = "entry/article/create.html"
    autofocus = 'p_name'



@login_required
def status_edit(request, pk: int):
    status: models.TEntry = get_object_or_404(
        models.TEntry.objects.select_related("t_post"), pk=pk
    )
    form = forms.UpdateStatusForm(request.POST or None, instance=status)

    if request.method == "POST":
        original_content = status.e_content
        if form.is_valid():
            form.prepare_data()
            send_webmention(request, form.instance.t_post, original_content)
            form.save()
            send_webmention(request, form.instance.t_post, form.instance.e_content)
            permalink_a_tag = render_to_string(
                "fragments/view_post_link.html", {"t_post": form.instance.t_post}
            )
            messages.success(request, f"Saved Status. {mark_safe(permalink_a_tag)}")
    context = {"form": form, "nav": "status"}
    return render(request, "entry/status_update.html", context=context)


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
def article_edit(request, pk: int):
    status: models.TEntry = get_object_or_404(
        models.TEntry.objects.select_related("t_post"), pk=pk
    )
    form = forms.UpdateArticleForm(request.POST or None, instance=status, autofocus='p_name')

    if request.method == "POST":
        original_content = status.e_content
        if form.is_valid():
            form.prepare_data()
            send_webmention(request, form.instance.t_post, original_content)
            form.save()
            send_webmention(request, form.instance.t_post, form.instance.e_content)
            permalink_a_tag = render_to_string(
                "fragments/view_post_link.html", {"t_post": form.instance.t_post}
            )
            messages.success(request, f"Saved Status. {mark_safe(permalink_a_tag)}")
    context = {"form": form, "nav": "status"}
    return render(request, "entry/article/update.html", context=context)


@login_required
def article_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects, pk=pk)
    send_webmention(request, status.t_post, status.e_content)
    status.delete()
    # TODO: Should we also delete the t_post ?
    messages.success(request, "Article Deleted")
    return redirect(resolve_url("status_list"))
