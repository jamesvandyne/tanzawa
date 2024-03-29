from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now
from django.views import generic
from meta import views as meta_views
from taggit import models as taggit_models

from application import entry as entry_application
from data.entry import models as entry_models
from data.indieweb.constants import MPostKinds, MPostStatuses
from data.post import models as post_models
from data.streams.models import MStream

from . import forms


def status_detail(request, uuid):
    t_post: post_models.TPost = get_object_or_404(
        post_models.TPost.objects.visible_for_user(request.user.id)
        .filter(m_post_status__key=MPostStatuses.published)
        .select_related(
            "m_post_kind",
            "ref_t_entry",
            "ref_t_entry__t_reply",
            "ref_t_entry__t_bookmark",
            "ref_t_entry__t_checkin",
            "ref_t_entry__t_location",
        )
        .prefetch_related("streams", "ref_t_entry__t_syndication"),
        uuid=uuid,
    )
    t_entry = t_post.ref_t_entry
    webmentions = t_post.ref_t_webmention.filter(approval_status=True).select_related("t_post", "t_webmention_response")
    detail_template = f"public/entry/{t_post.m_post_kind.key}_item.html"

    context = {
        "t_post": t_post,
        "detail_template": detail_template,
        "webmentions": webmentions,
        "webmentions_count": webmentions.count(),
        "t_entry": t_entry,
        "now": now(),
        "selected": [stream.slug for stream in t_post.streams.all()],
        "title": t_entry.p_name if t_entry.p_name else t_entry.p_summary[:140],
        "streams": MStream.objects.visible(request.user),
        "public": True,
        "meta": entry_application.get_open_graph_meta_for_entry(request, t_entry),
        "open_interactions": request.GET.get("o"),
    }
    return render(request, "public/post/post_detail.html", context=context)


class Bookmarks(generic.ListView):
    template_name = "public/entry/bookmarks.html"
    paginate_by = 5

    def get_queryset(self):
        qs = self._get_base_queryset()
        # Ensure all tags are wrapped in quotes to account for tags which are multiple words
        tag_names = " ".join([f'"{tag_name}"' for tag_name in self.request.GET._getlist("tag", [])])
        form = forms.BookmarksSearchForm({"tag": tag_names})
        if form.is_valid():
            if form.cleaned_data["tag"]:
                qs = qs.filter(t_post__tags__name__in=form.cleaned_data["tag"])
        return qs

    def _get_base_queryset(self):
        return (
            entry_models.TEntry.objects.visible_for_user(self.request.user.id)
            .select_related(
                "t_post",
                "t_post__m_post_kind",
                "t_post__p_author",
                "t_location",
                "t_bookmark",
            )
            .filter(t_post__m_post_status__key=MPostStatuses.published)
            .filter(t_post__m_post_kind__key=MPostKinds.bookmark)
            .exclude(t_post__visibility=post_models.Visibility.UNLISTED)
            .order_by("-t_post__dt_published")
            .distinct()
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update(
            {
                "selected": ["bookmarks"],
                "title": "Bookmarks",
                "tags": taggit_models.Tag.objects.filter(tpost__m_post_kind__key=MPostKinds.bookmark)
                .annotate(count=Count("tpost"))
                .order_by("name"),
                "meta": meta_views.Meta(
                    url=self.request.build_absolute_uri(),
                    secure_url=self.request.build_absolute_uri(),
                    title="Bookmarks",
                ),
            }
        )
        return context
