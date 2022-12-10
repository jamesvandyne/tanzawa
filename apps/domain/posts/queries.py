import datetime
from typing import List, Optional

from core.constants import Visibility
from data.indieweb.constants import MPostKinds, MPostStatuses
from data.post import models as post_models
from data.streams import models as stream_models
from django.contrib.auth import models as auth_models


def get_public_posts_for_user(
    user: Optional[auth_models.User],
    stream: Optional[stream_models.MStream] = None,
    kinds: Optional[List[MPostKinds]] = None,
):
    """
    This function gets all visible posts for a user sorted in reverse chronological order.
    """
    user_id = user.id if user else None
    posts = post_models.TPost.objects.visible_for_user(user_id=user_id)
    if stream:
        posts = posts.filter(streams=stream, m_post_status__key=MPostStatuses.published)
    else:
        posts = posts.filter(m_post_status__key=MPostStatuses.published)
    if kinds:
        posts = posts.filter(m_post_kind__key__in=kinds)
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


def get_last_post_with_location(
    user: Optional[auth_models.User],
    stream: Optional[stream_models.MStream] = None,
    kinds: Optional[List[MPostKinds]] = None,
) -> Optional[post_models.TPost]:
    """
    Return the latest post with a location.
    """
    return get_public_posts_for_user(user, stream, kinds).filter(ref_t_entry__t_location__isnull=False).first()


def is_published(post_id: int) -> bool:
    """
    Return if the post is published.
    """
    return (
        post_models.TPost.objects.filter(id=post_id).values_list("m_post_status__key", flat=True).first()
        == MPostStatuses.published
    )


def determine_published_at(post: post_models.TPost, occurred_at: datetime.datetime) -> datetime.datetime | None:
    if post.m_post_status.key == post_models.MPostStatuses.published:
        if post.dt_published is None or not is_published(post.id):
            return occurred_at
    return None
