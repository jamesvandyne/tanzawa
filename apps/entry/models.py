from core.models import TimestampModel
from django.db import models
from django.contrib.gis.db import models as geo_models
from indieweb.extract import LinkedPage, LinkedPageAuthor


class TEntry(TimestampModel):

    t_post = models.ForeignKey(
        "post.TPost", on_delete=models.CASCADE, related_name="ref_t_entry"
    )

    p_name = models.CharField(max_length=255, blank=True, default="")
    p_summary = models.CharField(max_length=1024, blank=True, default="")
    e_content = models.TextField(blank=True, default="")

    class Meta:
        db_table = "t_entry"

    def __str__(self):
        return f"{self.t_post}: {self.p_name}"


class TReply(TimestampModel):

    t_entry = models.OneToOneField(
        TEntry, on_delete=models.CASCADE, related_name="t_reply"
    )
    u_in_reply_to = models.URLField()
    title = models.CharField(max_length=128, blank=True, default="")
    quote = models.TextField(blank=True, default="")

    author = models.CharField(max_length=64, blank=True, default="")
    author_url = models.URLField(blank=True, default="")
    author_photo = models.URLField(blank=True, default="")

    class Meta:
        db_table = "t_reply"

    def __str__(self):
        return f"{self.t_entry} : {self.u_in_reply_to}"

    @property
    def linked_page(self) -> LinkedPage:
        return LinkedPage(
            url=self.u_in_reply_to,
            title=self.title,
            description=self.quote,
            author=LinkedPageAuthor(
                name=self.author, url=self.author_url, photo=self.author_photo
            ),
        )


class TBookmark(TimestampModel):

    t_entry = models.OneToOneField(
        TEntry, on_delete=models.CASCADE, related_name="t_bookmark"
    )
    u_bookmark_of = models.URLField()
    title = models.CharField(max_length=128, blank=True, default="")
    quote = models.TextField(blank=True, default="")

    author = models.CharField(max_length=64, blank=True, default="")
    author_url = models.URLField(blank=True, default="")
    author_photo = models.URLField(blank=True, default="")

    class Meta:
        db_table = "t_bookmark"

    def __str__(self):
        return f"{self.t_entry} : {self.u_bookmark_of}"

    @property
    def linked_page(self) -> LinkedPage:
        return LinkedPage(
            url=self.u_bookmark_of,
            title=self.title,
            description=self.quote,
            author=LinkedPageAuthor(
                name=self.author, url=self.author_url, photo=self.author_photo
            ),
        )


class TLocation(TimestampModel):
    t_entry = models.OneToOneField(
        TEntry, on_delete=models.CASCADE, related_name="t_location"
    )
    street_address = models.CharField(max_length=128, blank=True, default="")
    locality = models.CharField(max_length=128, blank=True, default="")
    region = models.CharField(max_length=64, blank=True, default="")
    country_name = models.CharField(max_length=64, blank=True, default="")
    postal_code = models.CharField(max_length=16, blank=True, default="")
    point = geo_models.PointField(geography=True, srid=3857)

    class Meta:
        db_table = "t_location"


class TCheckin(TimestampModel):
    t_entry = models.OneToOneField(
        TEntry, on_delete=models.CASCADE, related_name="t_checkin"
    )
    t_location = models.OneToOneField(
        TLocation, on_delete=models.CASCADE, related_name="t_checkin"
    )
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "t_checkin"
