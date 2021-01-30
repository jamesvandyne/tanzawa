from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from indieweb.models import TWebmention

from .models import TPost


@login_required
def dashboard(request):

    webmentions = TWebmention.objects.filter(approval_status=None).reverse()

    context = {
        "posts": TPost.objects.all(),
        "webmentions": webmentions,
        "unread_count": webmentions.count(),
        "nav": "dashboard",
    }
    return render(request, "post/dashboard.html", context)


