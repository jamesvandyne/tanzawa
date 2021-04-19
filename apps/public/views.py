from django.views.generic import ListView
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.utils.functional import cached_property
from django.utils.timezone import now
from entry.models import TEntry
from indieweb.constants import MPostStatuses
from post.models import TPost
from streams.models import MStream


class HomeView(ListView):
    template_name = "public/index.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            TEntry.objects.select_related(
                "t_post",
                "t_post__p_author",
                "t_location",
                "t_bookmark",
                "t_reply",
                "t_checkin",
            )
            .filter(t_post__m_post_status__key=MPostStatuses.published)
            .annotate(
                interaction_count=Count(
                    "t_post__ref_t_webmention",
                    filter=Q(t_post__ref_t_webmention__approval_status=True),
                )
            )
            .order_by("-t_post__dt_published")
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update(
            {
                "selected": ["home"],
                "streams": MStream.objects.visible(self.request.user),
            }
        )
        return context


def status_detail(request, uuid):
    t_post: TPost = get_object_or_404(
        TPost.objects.prefetch_related(
            "ref_t_entry",
            "ref_t_entry__t_reply",
            "ref_t_entry__t_location",
            "ref_t_entry__t_bookmark",
            "ref_t_entry__t_checkin",
            "ref_t_entry__t_syndication",
        ).filter(m_post_status__key=MPostStatuses.published),
        uuid=uuid,
    )
    webmentions = t_post.ref_t_webmention.filter(approval_status=True)
    detail_template = f"public/entry/{t_post.m_post_kind.key}_item.html"
    t_entry = t_post.ref_t_entry.all()[0]
    context = {
        "t_post": t_post,
        "detail_template": detail_template,
        "webmentions": webmentions,
        "webmentions_count": webmentions.count(),
        "t_entry": t_entry,
        "now": now(),
        "selected": t_post.streams.values_list("slug", flat=True),
        "title": t_entry.p_name if t_entry.p_name else t_entry.p_summary[:140],
        "streams": MStream.objects.visible(request.user),
        "public": True,
    }
    return render(request, "public/post/post_detail.html", context=context)


class AuthorDetail(ListView):
    template_name = "public/index.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            TEntry.objects.select_related(
                "t_post",
                "t_post__p_author",
                "t_location",
                "t_bookmark",
                "t_reply",
                "t_checkin",
            )
            .filter(
                t_post__m_post_status__key=MPostStatuses.published,
                t_post__p_author__username__exact=self.kwargs["username"],
            )
            .annotate(
                interaction_count=Count(
                    "t_post__ref_t_webmention",
                    filter=Q(t_post__ref_t_webmention__approval_status=True),
                )
            )
            .order_by("-t_post__dt_published")
        )


class StreamView(ListView):
    template_name = "public/index.html"
    paginate_by = 10

    @cached_property
    def stream(self):
        return get_object_or_404(
            MStream.objects.visible(self.request.user), slug=self.kwargs["stream_slug"]
        )

    def get_queryset(self):

        return (
            TEntry.objects.select_related(
                "t_post",
                "t_post__p_author",
                "t_location",
                "t_bookmark",
                "t_reply",
                "t_checkin",
            )
            .filter(t_post__in=self.stream.posts.published())
            .filter(t_post__m_post_status__key=MPostStatuses.published)
            .annotate(
                interaction_count=Count(
                    "t_post__ref_t_webmention",
                    filter=Q(t_post__ref_t_webmention__approval_status=True),
                )
            )
            .order_by("-t_post__dt_published")
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update(
            {
                "stream": self.stream,
                "selected": [self.stream.slug],
                "streams": MStream.objects.visible(self.request.user),
            }
        )
        return context
