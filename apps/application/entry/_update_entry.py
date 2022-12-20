import datetime

from core import constants
from data.entry import models as entry_models
from data.files import models as file_models
from data.indieweb import constants as indieweb_constants
from data.post import models as post_models
from data.streams import models as stream_models
from data.trips import models as trip_models
from django.db import transaction
from django.utils import timezone
from domain.entry import operations as entry_ops
from domain.entry import queries as entry_queries

from ._create_entry import Bookmark, Checkin, Location, Reply


class PostKindMismatch(Exception):
    pass


@transaction.atomic
def update_entry(
    entry_id: int,
    status: post_models.MPostStatus,
    visibility: constants.Visibility,
    title: str,
    content: str,
    published_at: datetime.datetime | None = None,
    streams: list[stream_models.MStream] | None = None,
    trip: trip_models.TTrip | None = None,
    syndication_urls: list[str] | None = None,
    location: Location | None = None,
    reply: Reply | None = None,
    bookmark: Bookmark | None = None,
    checkin: Checkin | None = None,
) -> entry_models.TEntry:
    """
    Create a new entry with related data.
    """
    entry = entry_models.TEntry.objects.get(pk=entry_id)
    _update_entry(
        entry=entry,
        status=status,
        visibility=visibility,
        title=title,
        content=content,
        published_at=published_at,
        streams=streams,
        trip=trip,
    )

    if syndication_urls is not None:
        _update_syndication_urls(entry, syndication_urls)

    if location:
        _update_location(entry, location)
    else:
        entry_ops.remove_location(entry)

    if reply:
        _update_reply(entry, reply)

    if bookmark:
        _update_bookmark(entry, bookmark)

    if checkin:
        _update_checkin(entry, checkin)

    return entry


def _update_entry(
    entry: entry_models.TEntry,
    status: post_models.MPostStatus,
    visibility: constants.Visibility,
    title: str,
    content: str,
    published_at: datetime.datetime | None = None,
    streams: list[stream_models.MStream] | None = None,
    trip: trip_models.TTrip | None = None,
) -> entry_models.TEntry:
    occurred_at = timezone.now()
    published_at = _determine_published_at(status, published_at)
    entry = entry_ops.update_entry(
        entry=entry,
        title=title,
        e_content=content,
        summary=entry_queries.get_summary(content),
        status=status,
        visibility=visibility,
        updated_at=occurred_at,
        published_at=published_at,
        files=_get_files_in_post(content),
        streams=streams,
        trip=trip,
    )
    return entry


def _update_reply(entry: entry_models.TEntry, reply: Reply) -> entry_models.TReply:
    entry_reply = entry.t_reply
    entry_reply.update(
        u_in_reply_to=reply.u_in_reply_to,
        title=reply.title,
        quote=reply.quote,
        author=reply.author,
        author_url=reply.author_url,
        author_photo=reply.author_photo,
    )
    return entry_reply


def _update_bookmark(entry: entry_models.TEntry, bookmark: Bookmark) -> entry_models.TBookmark:
    entry_bookmark = entry.t_bookmark
    entry_bookmark.update(
        u_bookmark_of=bookmark.u_bookmark_of,
        title=bookmark.title,
        quote=bookmark.quote,
        author=bookmark.author,
        author_url=bookmark.author_url,
        author_photo=bookmark.author_photo,
    )
    return entry_bookmark


def _update_location(entry: entry_models.TEntry, location: Location) -> entry_models.TLocation:
    try:
        entry_location = entry.t_location
    except entry_models.TLocation.DoesNotExist:
        return entry_models.TLocation.objects.create(
            t_entry=entry,
            street_address=location.street_address,
            locality=location.locality,
            region=location.region,
            country_name=location.country_name,
            postal_code=location.postal_code,
            point=location.point,
        )
    else:
        entry_location.change_location(
            street_address=location.street_address,
            locality=location.locality,
            region=location.region,
            country_name=location.country_name,
            postal_code=location.postal_code,
            point=location.point,
        )


def _update_checkin(entry: entry_models.TEntry, checkin: Checkin) -> entry_models.TCheckin:
    if not entry.is_checkin:
        raise PostKindMismatch(f"Cannot create checkin with post kind {entry.t_post.m_post_kind.key}")
    entry_checkin = entry.t_checkin
    entry_checkin.update_name_url(name=checkin.name, url=checkin.url)
    return entry_checkin


def _update_syndication_urls(entry: entry_models.TEntry, urls: list[str]) -> list[entry_models.TSyndication]:
    entry.t_syndication.all().delete()
    return [entry_models.TSyndication.objects.create(t_entry=entry, url=url) for url in urls]


def _get_files_in_post(content: str) -> list[file_models.TFile]:
    file_uuids = entry_queries.get_attachment_identifiers_in_content(content)
    return list(file_models.TFile.objects.filter(uuid__in=file_uuids))


def _determine_published_at(
    status: post_models.MPostStatus, published_at: datetime.datetime | None
) -> datetime.datetime | None:
    if published_at:
        return published_at
    if status.key == indieweb_constants.MPostStatuses.published:
        return timezone.now()
    return None
