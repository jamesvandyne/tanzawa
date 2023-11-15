from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import ListView, TemplateView

from core.constants import Visibility
from data.entry.models import TEntry
from data.indieweb.constants import MPostKinds, MPostStatuses
from data.post.models import MPostKind
from data.streams.models import MStream
from domain.files import queries as file_queries
from domain.indieweb.webmention import approved_webmentions
from domain.posts import queries as post_queries
from domain.sunbottle import queries as sunbotte_queries


class BlogListView(ListView):
    template_name = "public/index.html"
    paginate_by = 5

    def get_queryset(self):
        return (
            TEntry.objects.visible_for_user(self.request.user.id)
            .select_related(
                "t_post",
                "t_post__m_post_kind",
                "t_post__p_author",
                "t_location",
                "t_bookmark",
                "t_reply",
                "t_checkin",
            )
            .filter(t_post__m_post_status__key=MPostStatuses.published)
            .exclude(t_post__visibility=Visibility.UNLISTED)
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


class HomeView(TemplateView):
    template_name = "public/home.html"
    paginate_by = 5
    stream_name: str | None = None
    stream: MStream | None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.stream_name = settings.HIGHLIGHT_STREAM_SLUG
        try:
            self.stream = MStream.objects.get(slug=self.stream_name)
        except MStream.DoesNotExist:
            self.stream = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context.update(
            {
                "centered_nav": True,
                "selected": ["home"],
                "streams": MStream.objects.visible(self.request.user),
                "posts": post_queries.get_public_posts_for_user(
                    self.request.user, kinds=[MPostKinds.note, MPostKinds.reply, MPostKinds.bookmark]
                )[:3],
                "highlight_kind": {
                    "kind": MPostKind.objects.get(key=MPostKinds.article),
                    "posts": post_queries.get_public_posts_for_user(
                        self.request.user, kinds=[MPostKinds.article]
                    ).exclude(streams__slug=self.stream_name)[:5],
                },
                "highlight_stream": {
                    "posts": post_queries.get_public_posts_for_user(self.request.user, stream=self.stream)[:5],
                    "stream": self.stream,
                },
                "last_seen": {
                    "last_location_post": post_queries.get_last_post_with_location(self.request.user),
                    "checkins": zip(
                        post_queries.get_public_posts_for_user(self.request.user, kinds=[MPostKinds.checkin])[1:5],
                        ["text-lg", "text-md", "text-sm", "text-xs"],
                    ),
                },
                "photo_gallery": file_queries.get_public_photos(limit=10),
                "webmentions": approved_webmentions()[:10],
            }
        )
        if settings.SUNBOTTLE_API_URL:
            context["generation"] = sunbotte_queries.get_generation(timezone.now().time().hour)

        return context
