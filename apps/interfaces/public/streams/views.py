from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.generic import ListView

from core.constants import Visibility
from data.entry.models import TEntry
from data.indieweb.constants import MPostStatuses
from data.streams.models import MStream


class StreamView(ListView):
    template_name = "public/index.html"
    paginate_by = 10

    @cached_property
    def stream(self):
        return get_object_or_404(MStream.objects.visible(self.request.user), slug=self.kwargs["stream_slug"])

    def get_queryset(self):

        return (
            TEntry.objects.visible_for_user(self.request.user.id)
            .exclude(t_post__visibility=Visibility.UNLISTED)
            .select_related(
                "t_post",
                "t_post__m_post_kind",
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
