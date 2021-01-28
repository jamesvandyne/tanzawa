import mf2py
import mf2util
from django.shortcuts import render
from webmention.models import WebMentionResponse

from .models import TPost


def dashboard(request):
    webmentions = WebMentionResponse.objects.all().order_by("id").reverse()[:5]

    parsed_webmentions = []
    for wm in webmentions:
        parsed = mf2py.parse(doc=wm.response_body)
        comment = mf2util.interpret_comment(parsed, wm.source, [wm.response_to])
        comment.update({"reviewed": wm.reviewed, "id": wm.id, "source": wm.source})

        parsed_webmentions.append(comment)

    context = {
        "posts": TPost.objects.all(),
        "webmentions": parsed_webmentions,
        "unread_count": WebMentionResponse.objects.filter(reviewed=False).count(),
        "nav": "dashboard",
    }
    return render(request, "post/dashboard.html", context)
