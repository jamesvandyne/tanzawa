from django.db import models

from core.constants import VISIBILITY_CHOICES, Visibility
from core.models import TimestampModel


class MStreamManager(models.Manager):
    def visible(self, user):
        if user.is_authenticated:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(visibility=Visibility.PUBLIC)


class MStream(TimestampModel):

    icon = models.CharField(max_length=2, help_text="Select an emoji")
    name = models.CharField(max_length=32)
    slug = models.SlugField(unique=True)
    visibility = models.SmallIntegerField(choices=VISIBILITY_CHOICES, default=Visibility.PUBLIC)

    posts = models.ManyToManyField("post.TPost", through="TStreamPost", through_fields=("m_stream", "t_post"))
    objects = MStreamManager()

    class Meta:
        db_table = "m_stream"
        verbose_name = "Stream"
        verbose_name_plural = "Streams"

    def __str__(self):
        return self.name


class TStreamPost(TimestampModel):

    m_stream = models.ForeignKey(MStream, on_delete=models.CASCADE)
    t_post = models.ForeignKey("post.TPost", on_delete=models.CASCADE)

    class Meta:
        db_table = "t_stream_post"
        unique_together = ("m_stream", "t_post")
        verbose_name = "Stream-Post"
        verbose_name_plural = "Stream-Posts"
