import datetime
from dataclasses import dataclass

from django.contrib.auth import models as auth_models
from django.contrib.gis import geos
from django.db import transaction
from django.utils import timezone

from core import constants
from data.entry import models as entry_models
from data.files import models as file_models
from data.indieweb import constants as indieweb_constants
from data.post import models as post_models
from data.streams import models as stream_models
from data.trips import models as trip_models
from domain.entry import operations as entry_ops
from domain.entry import queries as entry_queries


class PostKindMismatch(Exception):
    pass


@dataclass
class Location:
    street_address: str
    locality: str
    region: str
    country_name: str
    postal_code: str
    point: geos.Point


@dataclass
class Reply:
    u_in_reply_to: str
    title: str
    quote: str
    author: str
    author_url: str
    author_photo: str


@dataclass
class Bookmark:
    u_bookmark_of: str
    title: str
    quote: str
    author: str
    author_url: str
    author_photo: str


@dataclass
class Checkin:
    url: str
    name: str


@transaction.atomic
def create_entry(
    status: post_models.MPostStatus,
    post_kind: post_models.MPostKind,
    author: auth_models.User,
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
    tags: list[str] | None = None,
) -> entry_models.TEntry:
    """
    Create a new entry with related data.
    """
    entry = _create_entry(
        status=status,
        post_kind=post_kind,
        author=author,
        visibility=visibility,
        title=title,
        content=content,
        published_at=published_at,
        streams=streams,
        trip=trip,
    )

    if syndication_urls:
        _create_syndication_urls(entry, syndication_urls)

    if tags is not None:
        entry.t_post.tags.set(tags, clear=True)

    if location:
        _create_location(entry, location)

    if reply:
        _create_reply(entry, reply)

    if bookmark:
        _create_bookmark(entry, bookmark)

    if checkin:
        _create_checkin(entry, checkin)

    return entry


def _create_entry(
    status: post_models.MPostStatus,
    post_kind: post_models.MPostKind,
    author: auth_models.User,
    visibility: constants.Visibility,
    title: str,
    content: str,
    published_at: datetime.datetime | None = None,
    streams: list[stream_models.MStream] | None = None,
    trip: trip_models.TTrip | None = None,
) -> entry_models.TEntry:
    occurred_at = timezone.now()
    published_at = _determine_published_at(status, published_at)
    entry = entry_ops.create_entry(
        title=title,
        e_content=content,
        summary=entry_queries.get_summary(content),
        status=status,
        post_kind=post_kind,
        author=author,
        visibility=visibility,
        updated_at=published_at or occurred_at,
        published_at=published_at,
        files=_get_files_in_post(content),
        streams=streams,
        trip=trip,
    )
    return entry


def _create_reply(entry: entry_models.TEntry, reply: Reply) -> entry_models.TReply:
    if not entry.is_reply:
        raise PostKindMismatch(f"Cannot create reply with post kind {entry.t_post.m_post_kind.key}")

    return entry_models.TReply.objects.create(
        t_entry=entry,
        u_in_reply_to=reply.u_in_reply_to,
        title=reply.title,
        quote=reply.quote,
        author=reply.author,
        author_url=reply.author_url,
        author_photo=reply.author_photo,
    )


def _create_bookmark(entry: entry_models.TEntry, bookmark: Bookmark) -> entry_models.TBookmark:
    if not entry.is_bookmark:
        raise PostKindMismatch(f"Cannot create bookmark with post kind {entry.t_post.m_post_kind.key}")

    return entry_models.TBookmark.objects.create(
        t_entry=entry,
        u_bookmark_of=bookmark.u_bookmark_of,
        title=bookmark.title,
        quote=bookmark.quote,
        author=bookmark.author,
        author_url=bookmark.author_url,
        author_photo=bookmark.author_photo,
    )


def _create_location(entry: entry_models.TEntry, location: Location) -> entry_models.TLocation:
    return entry_models.TLocation.objects.create(
        t_entry=entry,
        street_address=location.street_address,
        locality=location.locality,
        region=location.region,
        country_name=location.country_name,
        postal_code=location.postal_code,
        point=location.point,
    )


def _create_checkin(entry: entry_models.TEntry, checkin: Checkin) -> entry_models.TCheckin:
    if not entry.is_checkin:
        raise PostKindMismatch(f"Cannot create checkin with post kind {entry.t_post.m_post_kind.key}")

    return entry_models.TCheckin.objects.create(
        t_entry=entry,
        t_location=entry.t_location,
        url=checkin.url,
        name=checkin.name,
    )


def _create_syndication_urls(entry: entry_models.TEntry, urls: list[str]) -> list[entry_models.TSyndication]:
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
