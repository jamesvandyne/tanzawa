from typing import Optional

from core.constants import Visibility
from django.contrib.auth import models as auth_models
from indieweb.constants import MPostStatuses
from post.models import TPost
from streams.models import MStream


def get_public_posts_for_user(user: Optional[auth_models.User], stream: Optional[MStream] = None):
    """
    This function gets all visible posts for a user sorted in reverse chronological order.
    """
    user_id = user.id if user else None
    posts = TPost.objects.visible_for_user(user_id=user_id)
    if stream:
        posts = posts.filter(streams=stream, m_post_status__key=MPostStatuses.published)
    else:
        posts = posts.filter(m_post_status__key=MPostStatuses.published)
    return (
        posts.exclude(visibility=Visibility.UNLISTED)
        .select_related("ref_t_entry")
        .prefetch_related(
            "ref_t_entry",
            "ref_t_entry__t_reply",
            "ref_t_entry__t_location",
            "ref_t_entry__t_checkin",
        )
        .all()
        .order_by("-dt_published")
    )
