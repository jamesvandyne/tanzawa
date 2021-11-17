from typing import Optional

from core.constants import Visibility
from core.models import TimestampModel
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.db.models import Q
from indieweb.extract import LinkedPage, LinkedPageAuthor


class TEntryManager(models.Manager):
    def visible_for_user(self, user_id: Optional[int]):
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


class TCheckin(TimestampModel):
    t_entry = models.OneToOneField(TEntry, on_delete=models.CASCADE, related_name="t_checkin")
    t_location = models.OneToOneField(TLocation, on_delete=models.CASCADE, related_name="t_checkin")
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "t_checkin"
        verbose_name = "Checkin"
        verbose_name_plural = "Checkins"


class TSyndication(TimestampModel):
    t_entry = models.ForeignKey(TEntry, on_delete=models.CASCADE, related_name="t_syndication")
    url = models.URLField()

    class Meta:
        db_table = "t_syndication"
        unique_together = ["t_entry", "url"]
        verbose_name = "Syndication URL"
        verbose_name_plural = "Syndication URLs"
