from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.utils.timezone import now
from entry.models import TEntry
from indieweb.constants import MPostStatuses
from post.models import TPost

from django.db.models import Count, Q

def home(request):
    context = {
        "entries": TEntry.objects.select_related("t_post", "t_post__p_author").filter(
            t_post__m_post_status__key=MPostStatuses.published
        ).annotate(interaction_count=Count('t_post__ref_t_webmention', filter=Q(t_post__ref_t_webmention__approval_status=True)))
    }
    return render(request, "public/index.html", context=context)


def status_detail(request, uuid):
    t_post = get_object_or_404(
        TPost.objects.prefetch_related("ref_t_entry").filter(
            m_post_status__key=MPostStatuses.published
        ),
        uuid=uuid,
    )
    webmentions = t_post.ref_t_webmention.filter(approval_status=True)
    context = {
        "t_post": t_post,
        "webmentions": webmentions,
        "webmentions_count": webmentions.count(),
        "status": t_post.ref_t_entry.all()[0],
        "now": now(),
        "public": True,
    }
    return render(request, "public/post/post_detail.html", context=context)


def author(request, username: str):
    objs = get_list_or_404(
        TEntry.objects.select_related("t_post", "t_post__p_author").filter(
            t_post__m_post_status__key=MPostStatuses.published,
            t_post__p_author__username__exact=username,
        )
    )
    context = {"entries": objs}
    return render(request, "public/index.html", context=context)
