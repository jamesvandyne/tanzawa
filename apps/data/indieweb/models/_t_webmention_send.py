import datetime

from django.db import models

from core.models import TimestampModel


class TWebmentionSend(TimestampModel):
    t_post = models.ForeignKey("post.TPost", related_name="ref_t_webmention_send", on_delete=models.CASCADE)
    target = models.URLField()
    dt_sent = models.DateTimeField()
    success = models.BooleanField()
    response_body = models.JSONField(default=dict)

    class Meta:
        db_table = "t_webmention_send"
        unique_together = ("target", "t_post")
        verbose_name = "Sent Webmention"
        verbose_name_plural = "Sent Webmentions"

    def __str__(self):
        return self.target

    def set_send_results(
        self, success: bool, occurred_at: datetime.datetime, response_body: dict | None = None
    ) -> None:
        self.dt_sent = occurred_at
        self.success = success
        self.response_body = response_body or {}
        self.save()
