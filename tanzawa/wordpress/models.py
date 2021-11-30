import uuid

from core.models import TimestampModel
from django.db import models

from .upload import wordpress_upload_to


class TWordpress(TimestampModel):
    export_file = models.FileField(upload_to=wordpress_upload_to)
    filename = models.CharField(max_length=128)
    link = models.URLField()
    base_site_url = models.URLField()
    base_blog_url = models.URLField()

    class Meta:
        db_table = "t_wordpress"
        verbose_name = "Wordpress"
        verbose_name_plural = "Wordpress"

    def __str__(self):
        return self.filename


class TCategory(TimestampModel):
    t_wordpress = models.ForeignKey(TWordpress, on_delete=models.CASCADE, related_name="ref_t_category")
    name = models.CharField(max_length=64)
    nice_name = models.SlugField(max_length=64)

    m_stream = models.ForeignKey("streams.MStream", null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = "t_wordpress_category"
        verbose_name = "Wordpress Category"
        verbose_name_plural = "Wordpress Categories"

    def __str__(self):
        return self.name


class TPostFormat(TimestampModel):
    """Wordpress PostFormat: Status, Quote, Link etc..."""

    t_wordpress = models.ForeignKey(TWordpress, on_delete=models.CASCADE, related_name="ref_t_post_format")
    m_post_kind = models.ForeignKey(
        "post.MPostKind",
        on_delete=models.SET_NULL,
        related_name="ref_t_post_format",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=64)
    nice_name = models.SlugField(max_length=64)

    class Meta:
        db_table = "t_wordpress_post_format"
        verbose_name = "Wordpress Post Format"
        verbose_name_plural = "Wordpress Post Formats"

    def __str__(self):
        return self.name


class TPostKind(TimestampModel):
    """IndieWeb PostKind: Article', Bookmark, Note, Reply, Checkin, Photo"""

    t_wordpress = models.ForeignKey(TWordpress, on_delete=models.CASCADE, related_name="ref_t_post_kind")
    m_post_kind = models.ForeignKey(
        "post.MPostKind",
        on_delete=models.SET_NULL,
        related_name="ref_t_post_kind",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=32)
    nice_name = models.SlugField(max_length=64)

    class Meta:
        db_table = "t_wordpress_post_kind"
        verbose_name = "Wordpress Post Kind"
        verbose_name_plural = "Wordpress Post Kinds"

    def __str__(self):
        return self.name


class TWordpressPost(TimestampModel):
    t_wordpress = models.ForeignKey(TWordpress, on_delete=models.CASCADE, related_name="ref_t_wordpress_post")

    path = models.CharField(max_length=256, db_index=True)  # original db path
    guid = models.CharField(max_length=256)
    uuid = models.UUIDField(default=uuid.uuid4, db_index=True)

    t_post = models.ForeignKey("post.TPost", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "t_wordpress_post"
        verbose_name = "Wordpress Post"
        verbose_name_plural = "Wordpress Posts"


class TWordpressAttachment(TimestampModel):
    t_wordpress = models.ForeignKey(TWordpress, on_delete=models.CASCADE, related_name="ref_t_wordpress_attachment")

    guid = models.CharField(max_length=256)
    uuid = models.UUIDField(default=uuid.uuid4)
    link = models.URLField(blank=True)
    t_file = models.ForeignKey("files.TFile", on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = "t_wordpress_attachment"
        verbose_name = "Wordpress Attachment"
        verbose_name_plural = "Wordpress Attachments"
