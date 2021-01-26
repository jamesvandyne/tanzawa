from django.shortcuts import render

from .models import TPost
from webmention.models import WebMentionResponse


def dashboard(request):
    context = {
        "posts": TPost.objects.all(),
        "webmentions": WebMentionResponse.objects.all().order_by('id').reverse()[:5],
        "nav": 'dashboard',
    }
    return render(request, "post/dashboard.html", context)
