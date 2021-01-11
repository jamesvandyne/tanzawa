from core.models import TimestampModel
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.urls import reverse

from .upload import upload_to, resized_upload_to


class TFile(TimestampModel):
    file = models.FileField(upload_to=upload_to)
    uuid = models.UUIDField()
    filename = models.CharField(max_length=128)
    point = geo_models.PointField(blank=True, null=True)

    posts = models.ManyToManyField(
        "post.TPost", through="TFilePost", through_fields=("t_file", "t_post")
    )

    class Meta:
        db_table = "t_file"
        verbose_name = "File"

    def get_absolute_url(self):
        return reverse("get_media", args=[self.uuid])


class TFilePost(TimestampModel):

    t_file = models.ForeignKey(TFile, on_delete=models.CASCADE)
    t_post = models.ForeignKey("post.TPost", on_delete=models.CASCADE)

    class Meta:
        db_table = "t_file_post"
        verbose_name = "File-Post"


class TResizedImage(TimestampModel):

    file = models.FileField(upload_to=resized_upload_to)
    t_file = models.ForeignKey(TFile, on_delete=models.CASCADE)

    width = models.IntegerField()
    height = models.IntegerField()

    class Meta:
        db_table = "t_resized_image"
        verbose_name = "ResizedImage"
