from data.entry.models import TEntry
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from indieweb.models import TWebmention

from .models import TPost


@login_required
def dashboard(request):
    t_entry_select_related_fields = (
        "t_post",
        "t_post__m_post_kind",
        "t_post__p_author",
        "t_post__m_post_status",
        "t_location",
        "t_bookmark",
        "t_reply",
        "t_checkin",
    )
    webmentions = (
        TWebmention.objects.filter(approval_status=None).select_related("t_post", "t_webmention_response").reverse()
    )
    recent_post_ids = TPost.objects.published().order_by("-dt_published").values_list("pk", flat=True)[:5]
    draft_post_ids = TPost.objects.drafts().values_list("pk", flat=True)
    context = {
        "recent_posts": (
            TEntry.objects.filter(t_post__id__in=recent_post_ids)
            .select_related(*t_entry_select_related_fields)
            .order_by("-t_post__dt_published")
        ),
        "drafts": TEntry.objects.filter(t_post__id__in=draft_post_ids).select_related(*t_entry_select_related_fields),
        "webmentions": webmentions,
        "unread_count": webmentions.count(),
        "nav": "dashboard",
        "page_title": "Dashboard",
    }
    return render(request, "post/dashboard.html", context)
