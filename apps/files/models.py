from django.db import models
from django.contrib.gis.db import models as geo_models

from core.models import TimestampModel

from .upload import upload_to


class TFile(TimestampModel):
    file = models.FileField(upload_to=upload_to)
    filename = models.CharField(max_length=128)
    point = geo_models.PointField()

    posts = models.ManyToManyField("post.TPost", through="TFilePost", through_fields=("t_file", "t_post"))

    class Meta:
        db_table = "t_file"


class TFilePost(TimestampModel):

    t_file = models.ForeignKey(TFile, on_delete=models.CASCADE)
    t_post = models.ForeignKey("post.TPost", on_delete=models.CASCADE)

    class Meta:
        db_table = "t_file_post"
