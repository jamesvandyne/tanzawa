from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from indieweb.models import TWebmention

from .models import TPost
from entry.models import TEntry


@login_required
def dashboard(request):

    webmentions = TWebmention.objects.filter(approval_status=None).reverse()
    recent_post_ids = TPost.objects.published().order_by('-dt_published').values_list('pk', flat=True)[:5]
    draft_post_ids = TPost.objects.drafts().values_list('pk', flat=True)
    context = {
        "recent_posts": TEntry.objects.filter(t_post__id__in=recent_post_ids),
        "drafts": TEntry.objects.filter(t_post__id__in=draft_post_ids),
        "webmentions": webmentions,
        "unread_count": webmentions.count(),
        "nav": "dashboard",
    }
    return render(request, "post/dashboard.html", context)
