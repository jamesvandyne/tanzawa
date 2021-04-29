from typing import Dict, Any
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import mark_safe
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, FormView
from indieweb.constants import MPostStatuses, MPostKinds
from indieweb.webmentions import send_webmention
from indieweb.extract import extract_reply_details_from_url
from post.models import MPostKind
from turbo_response import TurboFrame, redirect_303

from . import forms, models


@method_decorator(login_required, name="dispatch")
class CreateEntryView(CreateView):
    autofocus = None
    redirect_url = "status_edit"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"p_author": self.request.user, "autofocus": self.autofocus})
        return kwargs

    def get_named_forms(self):
        return {
            "location": forms.TLocationModelForm(
                self.request.POST or None, prefix="location"
            ),
            "syndication": forms.TSyndicationModelInlineFormSet(
                self.request.POST or None, prefix="syndication"
            ),
        }

    def form_valid(self, form, named_forms=None):
        form.prepare_data()

        with transaction.atomic():
            entry = form.save()
            named_forms["syndication"].instance = entry
            for named_form in named_forms.values():
                named_form.prepare_data(entry)
                named_form.save()

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            send_webmention(self.request, entry.t_post, entry.e_content)

        permalink_a_tag = render_to_string(
            "fragments/view_post_link.html", {"t_post": entry.t_post}
        )
        messages.success(
            self.request,
            f"Saved {form.cleaned_data['m_post_kind']}. {mark_safe(permalink_a_tag)}",
        )
        return redirect_303(resolve_url(self.redirect_url, pk=entry.pk))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(nav="posts", **kwargs)
        if "named_forms" not in context:
            context["named_forms"] = self.get_named_forms()
        return context

    def form_invalid(self, form, named_forms=None):
        context = self.get_context_data(form=form, named_forms=named_forms)
        return render(self.request, self.template_name, context=context, status=422)

    def get(self, request, *args, **kwargs):
        self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = None
        form = self.get_form()
        named_forms = self.get_named_forms()

        if form.is_valid() and all(
            (named_form.is_valid() for named_form in named_forms.values())
        ):
            return self.form_valid(form, named_forms)
        else:
            return self.form_invalid(form, named_forms)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(nav="posts", **kwargs)
        if "named_forms" not in context:
            context["named_forms"] = self.get_named_forms()
        return context

    def get_named_forms(self):
        try:
            t_location = self.object.t_location
        except models.TLocation.DoesNotExist:
            t_location = None
        return {
            "location": forms.TLocationModelForm(
                self.request.POST or None, instance=t_location, prefix="location"
            ),
            "syndication": forms.TSyndicationModelInlineFormSet(
                self.request.POST or None, prefix="syndication", instance=self.object
            ),
        }

    def form_valid(self, form, named_forms=None):
        form.prepare_data()
        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            send_webmention(self.request, form.instance.t_post, self.original_content)

        with transaction.atomic():
            entry = form.save()

            for named_form in named_forms.values():
                named_form.prepare_data(entry)
                named_form.save()

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            send_webmention(self.request, form.instance.t_post, form.instance.e_content)

        permalink_a_tag = render_to_string(
            "fragments/view_post_link.html", {"t_post": form.instance.t_post}
        )
        messages.success(
            self.request,
            f"Saved {form.instance.t_post.m_post_kind.key}. {mark_safe(permalink_a_tag)}",
        )
        return redirect_303(self.request.build_absolute_uri())

    def get_response(self, context):
        return render(self.request, self.template_name, context=context)

    def form_invalid(self, form, named_forms=None):
        context = self.get_context_data(form=form, named_forms=named_forms)
        return render(self.request, self.template_name, context=context)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = self.get_object()
        form = self.get_form()
        named_forms = self.get_named_forms()

        if form.is_valid() and all(
            (named_form.is_valid() for named_form in named_forms.values())
        ):
            return self.form_valid(form, named_forms)
        else:
            return self.form_invalid(form, named_forms)


@method_decorator(login_required, name="dispatch")
class ExtractLinkedPageMetaView(FormView):
    form_class = forms.ExtractMetaForm
    success_form = forms.CreateReplyForm
    invalidate_template = None
    validate_template = None
    turbo_frame = ""
    url_key = ""

    def get_context_data(self, **kwargs):
        return super().get_context_data(nav="posts", **kwargs)

    def get_named_forms(self):
        return {
            "location": forms.TLocationModelForm(
                self.request.POST or None, prefix="location"
            ),
            "syndication": forms.TSyndicationModelInlineFormSet(prefix="syndication"),
        }

    def form_valid(self, form):
        linked_page = extract_reply_details_from_url(form.cleaned_data["url"])
        initial = {
            self.url_key: form.cleaned_data["url"],
            "title": form.cleaned_data["url"],
            "author": "",
            "summary": "",
        }
        if linked_page:
            initial.update(
                {
                    self.url_key: linked_page.url,
                    "title": linked_page.title,
                    "author": linked_page.author.name,
                    "summary": linked_page.description,
                }
            )
        context = self.get_context_data(
            form=self.success_form(initial=initial, p_author=self.request.user),
            named_forms=self.get_named_forms(),
        )
        return (
            TurboFrame(self.turbo_frame)
            .template(self.validate_template, context)
            .response(self.request)
        )

    def form_invalid(self, form):
        return render(
            self.request,
            self.invalidate_template,
            context=self.get_context_data(),
            status=422,
        )


# Note CRUD views


class CreateStatusView(CreateEntryView):
    form_class = forms.CreateStatusForm
    template_name = "entry/note/create.html"
    turbo_template_name = "entry/note/_create.html"


class UpdateStatusView(UpdateEntryView):
    form_class = forms.UpdateStatusForm
    template_name = "entry/note/update.html"
    m_post_kind = MPostKinds.note
    turbo_template_name = "entry/note/_update.html"


# Article CRUD views


class CreateArticleView(CreateEntryView):
    form_class = forms.CreateArticleForm
    template_name = "entry/article/create.html"
    autofocus = "p_name"
    redirect_url = "article_edit"


class UpdateArticleView(UpdateEntryView):
    form_class = forms.UpdateArticleForm
    template_name = "entry/article/update.html"
    m_post_kind = MPostKinds.article
    autofocus = "p_name"


# Checkin CRUD views

# Checkin Create is done via micropub


class UpdateCheckinView(UpdateEntryView):
    form_class = forms.UpdateCheckinForm
    template_name = "entry/checkin/update.html"
    m_post_kind = MPostKinds.checkin
    autofocus = "p_name"

    def get_named_forms(self):
        named_forms = super().get_named_forms()
        try:
            t_checkin = self.object.t_checkin
        except models.TCheckin.DoesNotExist:
            t_checkin = None
        named_forms["checkin"] = forms.TCheckinModelForm(
            self.request.POST or None, instance=t_checkin, prefix="checkin"
        )
        return named_forms


# Reply CRUD views


class CreateReplyView(CreateEntryView):
    template_name = "entry/reply/create.html"
    redirect_url = "reply_edit"

    def get_form_class(self):
        if self.request.method == "GET":
            return forms.ExtractMetaForm
        return forms.CreateReplyForm

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return (
            TurboFrame("reply-form")
            .template("entry/reply/_form.html", context)
            .response(self.request)
        )


@method_decorator(login_required, name="dispatch")
class ExtractReplyMetaView(ExtractLinkedPageMetaView):
    form_class = forms.ExtractMetaForm
    invalidate_template = "entry/reply/_linked_page_form.html"
    validate_template = "entry/reply/_form.html"
    url_key = "u_in_reply_to"
    turbo_frame = "reply-form"


class UpdateReplyView(UpdateEntryView):
    form_class = forms.UpdateReplyForm
    template_name = "entry/reply/update.html"
    m_post_kind = MPostKinds.reply
    autofocus = "e_content"


# Bookmarks


class CreateBookmarkView(CreateEntryView):
    template_name = "entry/bookmark/create.html"
    redirect_url = "bookmark_edit"

    def get_form_class(self):
        if self.request.method == "GET":
            return forms.ExtractMetaForm
        return forms.CreateBookmarkForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == "GET":
            kwargs["label"] = "What's the URL you're bookmarking?"
        return kwargs

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return (
            TurboFrame("bookmark-form")
            .template("entry/bookmark/_form.html", context)
            .response(self.request)
        )


@method_decorator(login_required, name="dispatch")
class ExtractBookmarkMetaView(ExtractLinkedPageMetaView):
    form_class = forms.ExtractMetaForm
    success_form = forms.CreateBookmarkForm
    invalidate_template = "entry/bookmark/_linked_page_form.html"
    validate_template = "entry/bookmark/_form.html"
    url_key = "u_bookmark_of"
    turbo_frame = "bookmark-form"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["label"] = "What's the URL you're bookmarking?"
        return kwargs


class UpdateBookmarkView(UpdateEntryView):
    form_class = forms.UpdateBookmarkForm
    template_name = "entry/bookmark/update.html"
    m_post_kind = MPostKinds.bookmark
    autofocus = "e_content"


@login_required
def status_detail(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related("t_post"), pk=pk)
    context = {"status": status, "nav": "posts"}
    return render(request, "entry/status_detail.html", context=context)


@login_required
def status_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects, pk=pk)
    send_webmention(request, status.t_post, status.e_content)
    status.delete()
    # TODO: Should we also delete the t_post ?
    messages.success(request, "Status Deleted")
    return redirect(resolve_url("posts"))


@method_decorator(login_required, name="dispatch")
class TEntryListView(ListView):
    template_name = "entry/posts.html"
    paginate_by = 10

    m_post_kind_key = None
    m_post_kind = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.m_post_kind_key:
            self.m_post_kind = get_object_or_404(MPostKind, key=self.m_post_kind_key)

    def get_template_names(self):
        if self.request.turbo.frame:
            return "entry/fragments/posts.html"
        return "entry/posts.html"

    def get_queryset(self):
        qs = models.TEntry.objects.all().select_related(
            "t_post",
            "t_post__m_post_status",
            "t_post__m_post_kind",
            "t_post__p_author",
            "t_location",
            "t_bookmark",
            "t_reply",
            "t_checkin",
        )
        if self.m_post_kind:
            qs = qs.filter(t_post__m_post_kind=self.m_post_kind)
        return qs.order_by("-created_at")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["nav"] = "posts"
        return context

    def render_to_response(self, context: Dict[str, Any], **response_kwargs):
        if self.request.turbo.frame:
            return (
                TurboFrame(self.request.turbo.frame)
                .template("entry/fragments/posts.html", context)
                .response(self.request)
            )
        return super().render_to_response(context, **response_kwargs)


@login_required
def article_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects, pk=pk)
    send_webmention(request, status.t_post, status.e_content)
    status.delete()
    # TODO: Should we also delete the t_post ?
    messages.success(request, "Article Deleted")
    return redirect(resolve_url("posts"))


@login_required
def edit_post(request, pk: int):
    t_entry = get_object_or_404(
        models.TEntry.objects.select_related("t_post", "t_post__m_post_kind"), pk=pk
    )
    if t_entry.t_post.m_post_kind.key == MPostKinds.article:
        return redirect(reverse("article_edit", args=[pk]))
    elif t_entry.t_post.m_post_kind.key == MPostKinds.note:
        return redirect(reverse("status_edit", args=[pk]))
    elif t_entry.t_post.m_post_kind.key == MPostKinds.reply:
        return redirect(reverse("reply_edit", args=[pk]))
    elif t_entry.t_post.m_post_kind.key == MPostKinds.bookmark:
        return redirect(reverse("bookmark_edit", args=[pk]))
    elif t_entry.t_post.m_post_kind.key == MPostKinds.checkin:
        return redirect(reverse("checkin_edit", args=[pk]))
    messages.error(request, "Unknown post type")
    return redirect(resolve_url("posts"))
