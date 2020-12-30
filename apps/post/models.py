from django.db import models

from core.models import TimestampModel


class MPostStatus(TimestampModel):

    key = models.CharField(max_length=12)

    class Meta:
        db_table = "m_post_status"

    def __str__(self):
        return self.key


class MPostKind(TimestampModel):

    key = models.CharField(max_length=16)

    class Meta:
        db_table = "m_post_kind"

    def __str__(self):
        return self.key


class TPost(TimestampModel):

    m_post_status = models.ForeignKey(MPostStatus, on_delete=models.CASCADE)
    m_post_kind = models.ForeignKey(MPostKind, on_delete=models.CASCADE)

    published = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "t_post"
