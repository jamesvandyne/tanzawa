from core.models import TimestampModel
from django.db import models


class TNow(TimestampModel):
    content = models.TextField(blank=True, default="", help_text="What are you focusing on _now_?")
    files = models.ManyToManyField("files.TFile", through="TFileNow")

    class Meta:
        verbose_name = "Now"
        verbose_name_plural = "Now"

    def set_content(self, content: str) -> None:
        self.content = content
        self.save()


class TFileNow(TimestampModel):
    t_file = models.ForeignKey("files.TFile", on_delete=models.CASCADE)
    t_now = models.ForeignKey(TNow, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "File-Now"
        verbose_name_plural = "File-Now"
