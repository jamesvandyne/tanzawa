import datetime

from core import constants
from data.entry import models as entry_models
from data.files import models as file_models
from data.post import models as post_models
from data.streams import models as stream_models
from data.trips import models as trip_models
from django.contrib.auth import models as auth_models
from django.db import transaction


@transaction.atomic
def create_entry(
    status: post_models.MPostStatus,
    post_kind: post_models.MPostKind,
    author: auth_models.User,
    visibility: constants.Visibility,
    updated_at: datetime.datetime,
    title: str = "",
    e_content: str = "",
    summary: str = "",
    files: list[file_models.TFile] | None = None,
    streams: list[stream_models.MStream] | None = None,
    trip: trip_models.TTrip | None = None,
    published_at: datetime.datetime | None = None,
):
    """
    Create a new entry and post.
    """

    post = post_models.TPost.objects.create(
        m_post_status=status,
        m_post_kind=post_kind,
        p_author=author,
        visibility=visibility,
        dt_published=published_at,
        dt_updated=updated_at,
    )

    entry = entry_models.TEntry.objects.create(
        t_post=post,
        e_content=e_content,
        p_summary=summary,
        p_name=title,
    )

    if files:
        post.files.set(files)

    if streams:
        post.streams.set(streams)

    if trip:
        post.trips.set([trip])

    return entry
