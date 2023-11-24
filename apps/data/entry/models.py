from django.contrib.gis import geos
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.db.models import Q

from application.indieweb.extract import LinkedPage, LinkedPageAuthor
from core.constants import Visibility
from core.models import TimestampModel
from data.indieweb import constants as indieweb_constants


class TEntryManager(models.Manager):
    def visible_for_user(self, user_id: int | None):
        qs = self.get_queryset()
        anon_ok_entries = Q(t_post__visibility__in=[Visibility.PUBLIC, Visibility.UNLISTED])
        if user_id:
            private_entries = Q(t_post__visibility=Visibility.PRIVATE, t_post__p_author_id=user_id)
            return qs.filter(anon_ok_entries | private_entries)
        return qs.filter(anon_ok_entries)


class TEntry(TimestampModel):
    t_post = models.OneToOneField("post.TPost", on_delete=models.CASCADE, related_name="ref_t_entry")

    p_name = models.CharField(max_length=255, blank=True, default="")
    p_summary = models.CharField(max_length=1024, blank=True, default="")
    e_content = models.TextField(blank=True, default="")

    objects = TEntryManager()

    class Meta:
        db_table = "t_entry"
        verbose_name = "Entry"
        verbose_name_plural = "Entries"

    def __str__(self):
        return f"{self.t_post}: {self.p_name}"

    @property
    def is_checkin(self) -> bool:
        return self.t_post.m_post_kind.key == indieweb_constants.MPostKinds.checkin

    @property
    def is_note(self) -> bool:
        return self.t_post.m_post_kind.key == indieweb_constants.MPostKinds.note

    @property
    def is_article(self) -> bool:
        return self.t_post.m_post_kind.key == indieweb_constants.MPostKinds.article

    @property
    def is_bookmark(self) -> bool:
        return self.t_post.m_post_kind.key == indieweb_constants.MPostKinds.bookmark

    @property
    def is_reply(self) -> bool:
        return self.t_post.m_post_kind.key == indieweb_constants.MPostKinds.reply

    def update_content_summary(self, e_content: str, p_summary: str) -> None:
        self.e_content = e_content
        self.p_summary = p_summary
        self.save()

    def update_title_content_summary(self, title: str, e_content: str, p_summary: str) -> None:
        self.p_name = title
        self.e_content = e_content
        self.p_summary = p_summary
        self.save()

    def new_bridgy_url(self, url: str) -> None:
        self.bridgy_publish_url.create(url=url)


class TReply(TimestampModel):
    t_entry = models.OneToOneField(TEntry, on_delete=models.CASCADE, related_name="t_reply")
    u_in_reply_to = models.URLField()
    title = models.CharField(max_length=128, blank=True, default="")
    quote = models.TextField(blank=True, default="")

    author = models.CharField(max_length=64, blank=True, default="")
    author_url = models.URLField(blank=True, default="")
    author_photo = models.URLField(blank=True, default="")

    class Meta:
        db_table = "t_reply"
        verbose_name = "Reply"
        verbose_name_plural = "Replies"

    def __str__(self):
        return f"{self.t_entry} : {self.u_in_reply_to}"

    @property
    def linked_page(self) -> LinkedPage:
        return LinkedPage(
            url=self.u_in_reply_to,
            title=self.title,
            description=self.quote,
            author=LinkedPageAuthor(name=self.author, url=self.author_url, photo=self.author_photo),
        )

    def update(
        self, u_in_reply_to: str, title: str, quote: str, author: str, author_url: str, author_photo: str
    ) -> None:
        self.u_in_reply_to = u_in_reply_to
        self.title = title
        self.quote = quote
        self.author = author
        self.author_url = author_url
        self.author_photo = author_photo
        self.save()


class TBookmark(TimestampModel):
    t_entry = models.OneToOneField(TEntry, on_delete=models.CASCADE, related_name="t_bookmark")
    u_bookmark_of = models.URLField()
    title = models.CharField(max_length=128, blank=True, default="")
    quote = models.TextField(blank=True, default="")

    author = models.CharField(max_length=64, blank=True, default="")
    author_url = models.URLField(blank=True, default="")
    author_photo = models.URLField(blank=True, default="")

    class Meta:
        db_table = "t_bookmark"
        verbose_name = "Bookmark"
        verbose_name_plural = "Bookmarks"

    def __str__(self):
        return f"{self.t_entry} : {self.u_bookmark_of}"

    @property
    def linked_page(self) -> LinkedPage:
        return LinkedPage(
            url=self.u_bookmark_of,
            title=self.title,
            description=self.quote,
            author=LinkedPageAuthor(name=self.author, url=self.author_url, photo=self.author_photo),
        )

    def update(
        self, u_bookmark_of: str, title: str, quote: str, author: str, author_url: str, author_photo: str
    ) -> None:
        self.u_bookmark_of = u_bookmark_of
        self.title = title
        self.quote = quote
        self.author = author
        self.author_url = author_url
        self.author_photo = author_photo
        self.save()


class TLocation(TimestampModel):
    t_entry = models.OneToOneField(TEntry, on_delete=models.CASCADE, related_name="t_location")
    street_address = models.CharField(max_length=128, blank=True, default="")
    locality = models.CharField(max_length=128, blank=True, default="")
    region = models.CharField(max_length=64, blank=True, default="")
    country_name = models.CharField(max_length=64, blank=True, default="")
    postal_code = models.CharField(max_length=16, blank=True, default="")
    point = geo_models.PointField(geography=True, srid=3857)

    class Meta:
        db_table = "t_location"
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    @property
    def summary(self):
        return (
            ", ".join(filter(None, [self.locality, self.region, self.country_name])) or f"{self.point.y},{self.point.x}"
        )

    def change_location(
        self, street_address: str, locality: str, region: str, country_name: str, postal_code: str, point: geos.Point
    ) -> None:
        self.street_address = street_address
        self.locality = locality
        self.region = region
        self.country_name = country_name
        self.postal_code = postal_code
        self.point = point
        self.save()


class TCheckin(TimestampModel):
    t_entry = models.OneToOneField(TEntry, on_delete=models.CASCADE, related_name="t_checkin")
    t_location = models.OneToOneField(TLocation, on_delete=models.CASCADE, related_name="t_checkin")
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "t_checkin"
        verbose_name = "Checkin"
        verbose_name_plural = "Checkins"

    def update_name_url(self, name: str, url: str) -> None:
        self.name = name
        self.url = url
        self.save()


class TSyndication(TimestampModel):
    t_entry = models.ForeignKey(TEntry, on_delete=models.CASCADE, related_name="t_syndication")
    url = models.URLField()

    class Meta:
        db_table = "t_syndication"
        unique_together = ["t_entry", "url"]
        verbose_name = "Syndication URL"
        verbose_name_plural = "Syndication URLs"


class BridgyPublishUrl(TimestampModel):
    """
    Determines which urls should be put into the post DOM so Bridgy can publish.
    """

    entry = models.ForeignKey(TEntry, on_delete=models.CASCADE, related_name="bridgy_publish_url")
    url = models.URLField()

    class Meta:
        unique_together = ["entry", "url"]
