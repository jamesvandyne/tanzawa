from core.constants import Visibility
from data.entry.models import TEntry
from django.db.models import Count, Q
from django.views.generic import ListView
from indieweb.constants import MPostStatuses


class AuthorDetail(ListView):
    template_name = "public/index.html"
    paginate_by = 10

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
