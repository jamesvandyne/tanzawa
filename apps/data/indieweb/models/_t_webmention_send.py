from django.db import models

from core.models import TimestampModel


class TWebmentionSend(TimestampModel):
    t_post = models.ForeignKey("post.TPost", related_name="ref_t_webmention_send", on_delete=models.CASCADE)
    target = models.URLField()
    dt_sent = models.DateTimeField()
    success = models.BooleanField()

    class Meta:
        db_table = "t_webmention_send"
        unique_together = ("target", "t_post")
        verbose_name = "Sent Webmention"
        verbose_name_plural = "Sent Webmentions"

    def __str__(self):
        return self.target
