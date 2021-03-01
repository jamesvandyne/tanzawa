from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from indieweb.models import TWebmention
from turbo_response import TurboFrame

from .models import TPost
from entry.models import TEntry


@login_required
def dashboard(request):

    webmentions = TWebmention.objects.filter(approval_status=None).reverse()
    recent_post_ids = (
        TPost.objects.published()
        .order_by("-dt_published")
        .values_list("pk", flat=True)[:5]
    )
    draft_post_ids = TPost.objects.drafts().values_list("pk", flat=True)
    context = {
        "recent_posts": TEntry.objects.filter(t_post__id__in=recent_post_ids).order_by(
            "-t_post__dt_published"
        ),
        "drafts": TEntry.objects.filter(t_post__id__in=draft_post_ids),
        "webmentions": webmentions,
        "unread_count": webmentions.count(),
        "nav": "dashboard",
    }
    if request.turbo.frame:
        return TurboFrame(request.turbo.frame).template("post/fragments/dashboard.html", context).response(request)
    return render(request, "post/dashboard.html", context)
