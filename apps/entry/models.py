from core.models import TimestampModel
from django.db import models


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
