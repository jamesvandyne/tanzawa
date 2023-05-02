from django.shortcuts import render

from core.constants import Visibility
from data.indieweb.constants import MPostKinds, MPostStatuses
from data.post.models import TPost


def cluster_map(request):
    posts = TPost.objects.visible_for_user(request.user.id).filter(
        m_post_status__key=MPostStatuses.published, m_post_kind__key=MPostKinds.checkin
    )
    if not request.user.is_authenticated:
        posts = posts.exclude(visibility=Visibility.UNLISTED)
    posts = posts.values("uuid", "ref_t_entry__t_checkin__name", "ref_t_entry__t_location__point")
    context = {"t_posts": posts, "selected": ["maps"], "title": "Checkin Cluster Map"}
    return render(request, "public/maps/cluster.html", context=context)
