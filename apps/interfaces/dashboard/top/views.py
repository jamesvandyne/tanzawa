from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from data.entry import models as entry_models
from data.indieweb.models import TWebmention
from data.post import models as post_models


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
    recent_post_ids = post_models.TPost.objects.published().order_by("-dt_published").values_list("pk", flat=True)[:5]
    draft_post_ids = post_models.TPost.objects.drafts().values_list("pk", flat=True)
    context = {
        "recent_posts": (
            entry_models.TEntry.objects.filter(t_post__id__in=recent_post_ids)
            .select_related(*t_entry_select_related_fields)
            .order_by("-t_post__dt_published")
        ),
        "drafts": entry_models.TEntry.objects.filter(t_post__id__in=draft_post_ids).select_related(
            *t_entry_select_related_fields
        ),
        "webmentions": webmentions,
        "unread_count": webmentions.count(),
        "nav": "dashboard",
        "page_title": "Dashboard",
    }
    return render(request, "post/dashboard.html", context)
