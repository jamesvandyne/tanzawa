import datetime

from django.contrib.auth import models as auth_models
from django.db import transaction

from core import constants
from data.entry import models as entry_models
from data.files import models as file_models
from data.post import models as post_models
from data.streams import models as stream_models
from data.trips import models as trip_models


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


@transaction.atomic
def update_entry(
    entry: entry_models.TEntry,
    status: post_models.MPostStatus,
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

    post = entry.t_post
    post.update_publishing_meta(
        post_status=status,
        visibility=visibility,
        dt_updated=updated_at,
        dt_published=published_at,
    )

    entry.update_title_content_summary(
        title=title,
        e_content=e_content,
        p_summary=summary,
    )

    if files:
        post.files.set(files)

    if streams:
        post.streams.set(streams)

    if trip:
        post.trips.set([trip])

    return entry


def remove_location(entry: entry_models.TEntry) -> None:
    """
    Remove a location from a given entry.
    """

    try:
        entry_location = entry.t_location
    except entry_models.TLocation.DoesNotExist:
        return None
    else:
        entry_location.delete()
