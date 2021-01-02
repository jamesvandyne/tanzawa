from django.shortcuts import render
from entry.models import TEntry
from indieweb.constants import MPostStatuses


def home(request):
    context = {
        'entries': TEntry.objects.select_related("t_post").filter(t_post__m_post_status__key=MPostStatuses.published)
    }
    return render(request, "public/index.html", context=context)