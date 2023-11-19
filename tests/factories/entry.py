from decimal import Decimal

import factory
from django.contrib.gis import geos

from data.entry import models


class StatusEntry(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TEntry

    p_name = ""
    p_summary = "Content here"
    e_content = "<h1>Content here</h1>"
    t_post = factory.SubFactory("tests.factories.PublishedNotePost")


class ArticleEntry(StatusEntry):
    p_name = "My title"
    t_post = factory.SubFactory("tests.factories.PublishedArticlePost")


class ReplyEntry(StatusEntry):
    p_name = "Reply to"
    t_post = factory.SubFactory("tests.factories.PublishedReplyPost")

    @factory.post_generation
    def reply(self, create, extracted, **kwargs):
        if not create:
            return

        reply = extracted or Reply(t_entry=self)
        self.t_reply = reply
        self.save()
        return reply


class BookmarkEntry(StatusEntry):
    p_name = "My bookmark"
    t_post = factory.SubFactory("tests.factories.PublishedBookmarkPost")

    @factory.post_generation
    def bookmark(self, create, extracted, **kwargs):
        if not create:
            return

        bookmark = extracted or Bookmark(t_entry=self)
        self.t_bookmark = bookmark
        self.save()
        return bookmark

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.t_post.tags.add(*extracted)


class CheckinEntry(StatusEntry):
    p_name = ""
    t_post = factory.SubFactory("tests.factories.PublishedCheckinPost")

    @factory.post_generation
    def checkin(self, create, extracted, **kwargs):
        if not create:
            return

        checkin = extracted or Checkin(t_entry=self, t_location__t_entry=self)
        self.t_checkin = checkin
        self.save()
        return checkin


class Location(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TLocation

    street_address = "123 ABC Road"
    locality = "Kawauchi"
    region = "Fukushima+Prefecture"
    country_name = "Japan"
    postal_code = ""

    point = geos.Point((Decimal("140.80078125000003"), Decimal("37.31425771585506")))
    t_entry = factory.SubFactory(StatusEntry)


class Bookmark(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TBookmark

    u_bookmark_of = "https://example.test"
    title = "Bookmark"
    quote = "Quote"

    author = "John Smith"
    author_url = "https://example.test/jsmith"
    author_photo = "https://example.test/jsmith/profile.png"


class Reply(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TReply

    u_in_reply_to = "https://example.test"
    title = "Reply"
    quote = "Quote"

    author = "John Smith"
    author_url = "https://example.test/jsmith"
    author_photo = "https://example.test/jsmith/profile.png"


class Checkin(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TCheckin

    t_location = factory.SubFactory(Location)
    t_entry = factory.SubFactory(
        CheckinEntry,
    )
    name = "Javahut"
    url = "https://javahut.test"
