import uuid

from core.models import TimestampModel
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from indieweb.constants import MPostStatuses


class MPostStatus(TimestampModel):

    key = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=16)

    class Meta:
        db_table = "m_post_status"

    def __str__(self):
        return self.name


class MPostKind(TimestampModel):

    key = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=16)

    class Meta:
        db_table = "m_post_kind"

    def __str__(self):
        return self.name


class TPostManager(models.Manager):
    def published(self):
        return (
            self
            .get_queryset()
            .filter(m_post_status__key=MPostStatuses.published, dt_published__lte=now())
        )


class TPost(TimestampModel):

    m_post_status = models.ForeignKey(MPostStatus, on_delete=models.CASCADE)
    m_post_kind = models.ForeignKey(MPostKind, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4)

    p_author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    dt_published = models.DateTimeField(blank=True, null=True)
    dt_updated = models.DateTimeField(blank=True, null=True)

    files = models.ManyToManyField(
        "files.TFile", through="files.TFilePost", through_fields=("t_post", "t_file")
    )
    streams = models.ManyToManyField(
        "streams.MStream",
        through="streams.TStreamPost",
        through_fields=("t_post", "m_stream"),
    )
    objects = TPostManager()

    class Meta:
        db_table = "t_post"

    def get_absolute_url(self):
        return reverse("public:post_detail", args=[self.uuid])
