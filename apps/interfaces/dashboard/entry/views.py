from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import mark_safe
from django.views.generic import (
    CreateView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from application import entry as entry_app
from application.indieweb import extract as indieweb_extract
from application.indieweb import webmentions
from data.entry import constants as entry_constants
from data.entry import models
from data.indieweb.constants import MPostKinds, MPostStatuses
from data.post import models as post_models
from domain.entry import queries as entry_queries
from interfaces.dashboard.entry import forms


@method_decorator(login_required, name="dispatch")
class CreateEntryView(CreateView):
    autofocus: str | None = None
    redirect_url = "status_edit"

    def setup(self, *args, **kwargs) -> None:
        super().setup(*args, **kwargs)
        self.object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"p_author": self.request.user, "autofocus": self.autofocus})
        return kwargs

    def get_named_forms(self):
        return {
            "location": forms.TLocationModelForm(self.request.POST or None, prefix="location"),
            "syndication": forms.TSyndicationModelInlineFormSet(self.request.POST or None, prefix="syndication"),
        }

    def get_redirect_url(self, entry) -> str:
        return resolve_url(self.redirect_url, pk=entry.pk)

    def form_valid(self, form, named_forms=None):
        entry = entry_app.create_entry(
            status=form.cleaned_data["m_post_status"],
            post_kind=form.cleaned_data["m_post_kind"],
            author=form.p_author,
            visibility=form.cleaned_data["visibility"],
            title=form.cleaned_data["p_name"],
            content=form.cleaned_data["e_content"],
            streams=form.cleaned_data["streams"],
            trip=form.cleaned_data["t_trip"],
            location=self._get_location(named_forms["location"]),
            syndication_urls=self._get_syndication_urls(named_forms["syndication"]),
        )

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, entry.t_post, entry.e_content)

        permalink_a_tag = render_to_string("fragments/view_post_link.html", {"t_post": entry.t_post})
        messages.success(
            self.request,
            f"Saved {form.cleaned_data['m_post_kind']}. {mark_safe(permalink_a_tag)}",
        )
        return redirect(self.get_redirect_url(entry=entry))

    def _get_location(self, location_form) -> entry_app.Location | None:
        if location_form.cleaned_data["point"]:
            return entry_app.Location(
                street_address=location_form.cleaned_data["street_address"],
                locality=location_form.cleaned_data["locality"],
                region=location_form.cleaned_data["region"],
                country_name=location_form.cleaned_data["country_name"],
                postal_code=location_form.cleaned_data["postal_code"],
                point=location_form.cleaned_data["point"],
            )
        return None

    def _get_syndication_urls(self, syndication_formset) -> list[str]:
        return [
            syndication_form.cleaned_data["url"]
            for syndication_form in syndication_formset
            if syndication_form.cleaned_data.get("url")
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(nav="posts", **kwargs)
        if "named_forms" not in context:
            context["named_forms"] = self.get_named_forms()
        context["page_title"] = "Create Post"
        return context

    def form_invalid(self, form, named_forms=None):
        context = self.get_context_data(form=form, named_forms=named_forms)
        return render(self.request, self.template_name, context=context, status=422)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = None
        form = self.get_form()
        named_forms = self.get_named_forms()

        if form.is_valid() and all(named_form.is_valid() for named_form in named_forms.values()):
            return self.form_valid(form, named_forms)
        else:
            return self.form_invalid(form, named_forms)


@method_decorator(login_required, name="dispatch")
class UpdateEntryView(UpdateView):
    m_post_kind = None
    original_content = ""

    def get_queryset(self):
        return models.TEntry.objects.select_related("t_post").filter(t_post__m_post_kind__key=self.m_post_kind)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        self.original_content = obj.e_content
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(nav="posts", **kwargs)
        if "named_forms" not in context:
            context["named_forms"] = self.get_named_forms()
        context["page_title"] = "Edit Post"
        return context

    def get_named_forms(self):
        try:
            t_location = self.object.t_location
        except models.TLocation.DoesNotExist:
            t_location = None
        return {
            "location": forms.TLocationModelForm(self.request.POST or None, instance=t_location, prefix="location"),
            "syndication": forms.TSyndicationModelInlineFormSet(
                self.request.POST or None, prefix="syndication", instance=self.object
            ),
        }

    def form_valid(self, form, named_forms=None):
        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, form.instance.t_post, self.original_content)

        entry_app.update_entry(
            entry_id=self.object.pk,
            status=form.cleaned_data["m_post_status"],
            visibility=form.cleaned_data["visibility"],
            title=form.cleaned_data["p_name"],
            content=form.cleaned_data["e_content"],
            streams=form.cleaned_data["streams"],
            trip=form.cleaned_data["t_trip"],
            location=self._get_location(named_forms["location"]),
            published_at=self.object.t_post.dt_published,
            syndication_urls=self._get_syndication_urls(named_forms["syndication"]),
        )

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, form.instance.t_post, form.instance.e_content)

        permalink_a_tag = render_to_string("fragments/view_post_link.html", {"t_post": form.instance.t_post})
        messages.success(
            self.request,
            f"Saved {form.instance.t_post.m_post_kind.key}. {mark_safe(permalink_a_tag)}",
        )
        return redirect(self.request.build_absolute_uri())

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

        if form.is_valid() and all(named_form.is_valid() for named_form in named_forms.values()):
            return self.form_valid(form, named_forms)
        else:
            return self.form_invalid(form, named_forms)

    def _get_location(self, location_form) -> entry_app.Location | None:
        if location_form.cleaned_data["point"]:
            return entry_app.Location(
                street_address=location_form.cleaned_data["street_address"],
                locality=location_form.cleaned_data["locality"],
                region=location_form.cleaned_data["region"],
                country_name=location_form.cleaned_data["country_name"],
                postal_code=location_form.cleaned_data["postal_code"],
                point=location_form.cleaned_data["point"],
            )
        return None

    def _get_syndication_urls(self, syndication_formset) -> list[str]:
        return [
            syndication_form.cleaned_data["url"]
            for syndication_form in syndication_formset
            if syndication_form.cleaned_data.get("url")
        ]


@method_decorator(login_required, name="dispatch")
class ExtractLinkedPageMetaView(FormView):
    form_class = forms.ExtractMetaForm
    success_form = forms.CreateReplyForm
    invalidate_template: str | None = None
    validate_template: str | None = None
    url_key = ""

    def get_context_data(self, **kwargs):
        return super().get_context_data(nav="posts", **kwargs)

    def get_named_forms(self):
        return {
            "location": forms.TLocationModelForm(self.request.POST or None, prefix="location"),
            "syndication": forms.TSyndicationModelInlineFormSet(prefix="syndication"),
        }

    def form_valid(self, form):
        linked_page = indieweb_extract.extract_reply_details_from_url(form.cleaned_data["url"])
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
        return TemplateResponse(self.request, self.validate_template, context)

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


class UpdateStatusView(UpdateEntryView):
    form_class = forms.UpdateStatusForm
    template_name = "entry/note/update.html"
    m_post_kind = MPostKinds.note


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

    def form_valid(self, form, named_forms=None):
        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, form.instance.t_post, self.original_content)

        entry_app.update_entry(
            entry_id=self.object.pk,
            status=form.cleaned_data["m_post_status"],
            visibility=form.cleaned_data["visibility"],
            title=form.cleaned_data["p_name"],
            content=form.cleaned_data["e_content"],
            streams=form.cleaned_data["streams"],
            trip=form.cleaned_data["t_trip"],
            location=self._get_location(named_forms["location"]),
            published_at=self.object.t_post.dt_published,
            syndication_urls=self._get_syndication_urls(named_forms["syndication"]),
            checkin=entry_app.Checkin(
                name=named_forms["checkin"].cleaned_data["name"],
                url=named_forms["checkin"].cleaned_data["url"],
            ),
        )

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, form.instance.t_post, form.instance.e_content)

        permalink_a_tag = render_to_string("fragments/view_post_link.html", {"t_post": form.instance.t_post})
        messages.success(
            self.request,
            f"Saved {form.instance.t_post.m_post_kind.key}. {mark_safe(permalink_a_tag)}",
        )
        return redirect(self.request.build_absolute_uri())


# Reply CRUD views


class CreateReplyView(CreateEntryView):
    template_name = "entry/reply/create.html"
    redirect_url = "reply_edit"

    def get_form_class(self):
        if self.request.method == "GET":
            return forms.ExtractMetaForm
        return forms.CreateReplyForm

    def form_valid(self, form, named_forms=None):
        entry = entry_app.create_entry(
            status=form.cleaned_data["m_post_status"],
            post_kind=form.cleaned_data["m_post_kind"],
            author=form.p_author,
            visibility=form.cleaned_data["visibility"],
            title=form.cleaned_data["p_name"],
            content=form.cleaned_data["e_content"],
            streams=form.cleaned_data["streams"],
            trip=form.cleaned_data["t_trip"],
            location=self._get_location(named_forms["location"]),
            syndication_urls=self._get_syndication_urls(named_forms["syndication"]),
            reply=entry_app.Reply(
                u_in_reply_to=form.cleaned_data["u_in_reply_to"],
                title=form.cleaned_data["title"],
                quote=form.cleaned_data["summary"],
                author=form.cleaned_data["author"],
                author_url=form.cleaned_data["author_url"],
                author_photo=form.cleaned_data["author_photo_url"],
            ),
        )

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, entry.t_post, entry.e_content)

        permalink_a_tag = render_to_string("fragments/view_post_link.html", {"t_post": entry.t_post})
        messages.success(
            self.request,
            f"Saved {form.cleaned_data['m_post_kind']}. {mark_safe(permalink_a_tag)}",
        )
        return redirect(self.get_redirect_url(entry=entry))

    def form_invalid(self, form, named_forms):
        context = self.get_context_data(form=form)
        return TemplateResponse(self.request, "entry/reply/_form.html", context)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, submit_form=forms.PublishStatusVisibilityForm())


@method_decorator(login_required, name="dispatch")
class ExtractReplyMetaView(ExtractLinkedPageMetaView):
    form_class = forms.ExtractMetaForm
    invalidate_template = "entry/reply/_linked_page_form.html"
    validate_template = "entry/reply/_form.html"
    url_key = "u_in_reply_to"


class UpdateReplyView(UpdateEntryView):
    form_class = forms.UpdateReplyForm
    template_name = "entry/reply/update.html"
    m_post_kind = MPostKinds.reply
    autofocus = "e_content"

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.reply = get_object_or_404(models.TReply, t_entry_id=kwargs["pk"])

    def form_valid(self, form, named_forms=None):
        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, form.instance.t_post, self.original_content)

        entry_app.update_entry(
            entry_id=self.object.pk,
            status=form.cleaned_data["m_post_status"],
            visibility=form.cleaned_data["visibility"],
            title=form.cleaned_data["p_name"],
            content=form.cleaned_data["e_content"],
            streams=form.cleaned_data["streams"],
            trip=form.cleaned_data["t_trip"],
            location=self._get_location(named_forms["location"]),
            published_at=self.object.t_post.dt_published,
            syndication_urls=self._get_syndication_urls(named_forms["syndication"]),
            reply=entry_app.Reply(
                u_in_reply_to=self.reply.u_in_reply_to,
                title=self.reply.title,
                quote=form.cleaned_data["summary"],
                author=self.reply.author,
                author_url=self.reply.author_url,
                author_photo=self.reply.author_photo,
            ),
        )

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, form.instance.t_post, form.instance.e_content)

        permalink_a_tag = render_to_string("fragments/view_post_link.html", {"t_post": form.instance.t_post})
        messages.success(
            self.request,
            f"Saved {form.instance.t_post.m_post_kind.key}. {mark_safe(permalink_a_tag)}",
        )
        return redirect(self.request.build_absolute_uri())


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

    def form_valid(self, form, named_forms=None):
        entry = entry_app.create_entry(
            status=form.cleaned_data["m_post_status"],
            post_kind=form.cleaned_data["m_post_kind"],
            author=form.p_author,
            visibility=form.cleaned_data["visibility"],
            title=form.cleaned_data["p_name"],
            content=form.cleaned_data["e_content"],
            streams=form.cleaned_data["streams"],
            trip=form.cleaned_data["t_trip"],
            location=self._get_location(named_forms["location"]),
            syndication_urls=self._get_syndication_urls(named_forms["syndication"]),
            bookmark=entry_app.Bookmark(
                u_bookmark_of=form.cleaned_data["u_bookmark_of"],
                title=form.cleaned_data["title"],
                quote=form.cleaned_data["summary"],
                author=form.cleaned_data["author"],
                author_url=form.cleaned_data["author_url"],
                author_photo=form.cleaned_data["author_photo_url"],
            ),
            tags=form.cleaned_data["tags"],
        )

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, entry.t_post, entry.e_content)

        permalink_a_tag = render_to_string("fragments/view_post_link.html", {"t_post": entry.t_post})
        messages.success(
            self.request,
            f"Saved {form.cleaned_data['m_post_kind']}. {mark_safe(permalink_a_tag)}",
        )
        return redirect(self.get_redirect_url(entry=entry))

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return TemplateResponse(self.request, "entry/bookmark/_form.html", context)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, submit_form=forms.PublishStatusVisibilityForm())


@method_decorator(login_required, name="dispatch")
class ExtractBookmarkMetaView(ExtractLinkedPageMetaView):
    form_class = forms.ExtractMetaForm
    success_form = forms.CreateBookmarkForm
    invalidate_template = "entry/bookmark/_linked_page_form.html"
    validate_template = "entry/bookmark/_form.html"
    url_key = "u_bookmark_of"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["label"] = "What's the URL you're bookmarking?"
        return kwargs


class UpdateBookmarkView(UpdateEntryView):
    form_class = forms.UpdateBookmarkForm
    template_name = "entry/bookmark/update.html"
    m_post_kind = MPostKinds.bookmark
    autofocus = "e_content"

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.bookmark = get_object_or_404(models.TBookmark, t_entry_id=kwargs["pk"])

    def form_valid(self, form, named_forms=None):
        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, form.instance.t_post, self.original_content)

        entry_app.update_entry(
            entry_id=self.object.pk,
            status=form.cleaned_data["m_post_status"],
            visibility=form.cleaned_data["visibility"],
            title=form.cleaned_data["p_name"],
            content=form.cleaned_data["e_content"],
            streams=form.cleaned_data["streams"],
            trip=form.cleaned_data["t_trip"],
            location=self._get_location(named_forms["location"]),
            syndication_urls=self._get_syndication_urls(named_forms["syndication"]),
            published_at=self.object.t_post.dt_published,
            bookmark=entry_app.Bookmark(
                u_bookmark_of=form.cleaned_data["u_bookmark_of"],
                title=form.cleaned_data["title"],
                quote=form.cleaned_data["summary"],
                author=self.bookmark.author,
                author_url=self.bookmark.author_url,
                author_photo=self.bookmark.author_photo,
            ),
            tags=form.cleaned_data["tags"],
        )

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmentions.send_webmention(self.request, form.instance.t_post, form.instance.e_content)

        permalink_a_tag = render_to_string("fragments/view_post_link.html", {"t_post": form.instance.t_post})
        messages.success(
            self.request,
            f"Saved {form.instance.t_post.m_post_kind.key}. {mark_safe(permalink_a_tag)}",
        )
        return redirect(self.request.build_absolute_uri())


@login_required
def status_detail(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related("t_post"), pk=pk)
    context = {"status": status, "nav": "posts"}
    return render(request, "entry/status_detail.html", context=context)


@login_required
def status_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects, pk=pk)
    webmentions.send_webmention(request, status.t_post, status.e_content)
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
            self.m_post_kind = get_object_or_404(post_models.MPostKind, key=self.m_post_kind_key)

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
        context.update(
            {
                "nav": "posts",
                "page_title": "Posts",
            }
        )
        return context


@login_required
def article_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects, pk=pk)
    webmentions.send_webmention(request, status.t_post, status.e_content)
    status.delete()
    # TODO: Should we also delete the t_post ?
    messages.success(request, "Article Deleted")
    return redirect(resolve_url("posts"))


@login_required
def edit_post(request, pk: int):
    t_entry = get_object_or_404(models.TEntry.objects.select_related("t_post", "t_post__m_post_kind"), pk=pk)
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


class QuickEntry(CreateStatusView):
    """
    Mobile optimized post only view.
    """

    template_name = "entry/note/quick.html"
    form_class = forms.QuickCreateStatusForm

    def get_redirect_url(self, entry):
        # Facilitate another quick post by redirecting to an empty quick entry form
        return reverse("status_quick")


@method_decorator(login_required, name="dispatch")
class ReplyTitle(TemplateView):
    template_name = "interfaces/dashboard/entry/reply/_reply_title.html"
    reply: models.TReply

    def setup(self, *args, pk: int, **kwargs):
        super().setup(*args, **kwargs)
        self.reply = get_object_or_404(models.TReply, t_entry_id=pk)

    def get_context_data(self, **kwargs) -> dict[str, str]:
        return super().get_context_data(
            title=self.reply.title, url=self.reply.u_in_reply_to, t_entry_id=self.reply.t_entry_id
        )


@method_decorator(login_required, name="dispatch")
class ChangeReplyTitle(FormView):
    template_name = "interfaces/dashboard/entry/reply/_change_reply_title.html"
    form_class = forms.ReplyTitle
    reply: models.TReply

    def setup(self, *args, pk: int, **kwargs):
        super().setup(*args, **kwargs)
        self.reply = get_object_or_404(models.TReply, t_entry_id=pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"initial": {"title": self.reply.title, "u_in_reply_to": self.reply.u_in_reply_to}})
        return kwargs

    def get_context_data(self, *args, **kwargs) -> dict[str, Any]:
        return super().get_context_data(*args, t_entry_id=self.reply.t_entry_id, **kwargs)

    def form_valid(self, form):
        self.reply.update(
            u_in_reply_to=form.cleaned_data["u_in_reply_to"],
            title=form.cleaned_data["title"],
            quote=self.reply.quote,
            author=self.reply.author,
            author_url=self.reply.author_url,
            author_photo=self.reply.author_photo,
        )
        return TemplateResponse(
            self.request,
            "interfaces/dashboard/entry/reply/_reply_title.html",
            {
                "t_entry_id": self.reply.t_entry_id,
                "title": form.cleaned_data["title"],
                "url": form.cleaned_data["u_in_reply_to"],
            },
        )


@method_decorator(login_required, name="dispatch")
class BookmarkTitle(TemplateView):
    template_name = "interfaces/dashboard/entry/bookmark/_bookmark_title.html"
    bookmark: models.TBookmark

    def setup(self, *args, pk: int, **kwargs):
        super().setup(*args, **kwargs)
        self.bookmark = get_object_or_404(models.TBookmark, t_entry_id=pk)

    def get_context_data(self, **kwargs) -> dict[str, str]:
        return super().get_context_data(
            title=self.bookmark.title, url=self.bookmark.u_bookmark_of, t_entry_id=self.bookmark.t_entry_id
        )


@method_decorator(login_required, name="dispatch")
class ChangeBookmarkTitle(FormView):
    template_name = "interfaces/dashboard/entry/bookmark/_change_bookmark_title.html"
    form_class = forms.BookmarkTitle
    bookmark: models.TBookmark

    def setup(self, *args, pk: int, **kwargs):
        super().setup(*args, **kwargs)
        self.bookmark = get_object_or_404(models.TBookmark, t_entry_id=pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"initial": {"title": self.bookmark.title, "u_bookmark_of": self.bookmark.u_bookmark_of}})
        return kwargs

    def get_context_data(self, *args, **kwargs) -> dict[str, Any]:
        return super().get_context_data(*args, t_entry_id=self.bookmark.t_entry_id, **kwargs)

    def form_valid(self, form):
        self.bookmark.update(
            u_bookmark_of=form.cleaned_data["u_bookmark_of"],
            title=form.cleaned_data["title"],
            quote=self.bookmark.quote,
            author=self.bookmark.author,
            author_url=self.bookmark.author_url,
            author_photo=self.bookmark.author_photo,
        )
        return TemplateResponse(
            self.request,
            "interfaces/dashboard/entry/bookmark/_bookmark_title.html",
            {
                "t_entry_id": self.bookmark.t_entry_id,
                "title": form.cleaned_data["title"],
                "url": form.cleaned_data["u_bookmark_of"],
            },
        )


@method_decorator(login_required, name="dispatch")
class SendToBridgy(FormView):
    template_name = "interfaces/dashboard/entry/bridgy/_form.html"
    form_class = forms.SendToBridgy
    entry: models.TEntry

    def setup(self, *args, pk: int, **kwargs):
        super().setup(*args, **kwargs)
        self.entry = get_object_or_404(models.TEntry, pk=pk)

    def get_context_data(self, *args, **kwargs) -> dict[str, Any]:
        return super().get_context_data(
            *args,
            t_entry_id=self.entry.id,
            is_syndicated_to_mastodon=entry_queries.is_syndicated_to_mastodon(self.entry),
            syndication_url=entry_queries.mastodon_syndication_url(self.entry),
            **kwargs,
        )

    def form_valid(self, form):
        entry_app.post_to_bridgy(
            t_entry=self.entry,
            entry_absolute_url=self.request.build_absolute_uri(self.entry.t_post.get_absolute_url()),
            target_bridgy_url=entry_constants.BridgySyndicationUrls.mastodon,
        )
        return TemplateResponse(
            self.request,
            "interfaces/dashboard/entry/bridgy/_form.html",
            {
                "t_entry_id": self.entry.id,
                "is_syndicated_to_mastodon": entry_queries.is_syndicated_to_mastodon(self.entry),
                "syndication_url": entry_queries.mastodon_syndication_url(self.entry),
            },
        )
