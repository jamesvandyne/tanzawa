from typing import TYPE_CHECKING, Optional

from core.models import TimestampModel
from django.db import models
from picklefield import PickledObjectField
from webmention.models import WebMentionResponse

if TYPE_CHECKING:
    from post import models as post_models


class TWebmention(TimestampModel):

    t_webmention_response = models.ForeignKey(
        WebMentionResponse, related_name="ref_t_webmention", on_delete=models.CASCADE
    )
    t_post = models.ForeignKey("post.TPost", related_name="ref_t_webmention", on_delete=models.CASCADE)
    approval_status = models.BooleanField(null=True, blank=True)
    microformat_data = PickledObjectField()

    class Meta:
        db_table = "t_webmention"
        unique_together = ("t_webmention_response", "t_post")
        verbose_name = "Webmention Approval"
        verbose_name_plural = "Webmention Approvals"

    def __str__(self):
        return f"{self.t_post} {self.t_webmention_response}"

    @classmethod
    def new(
        cls,
        t_webmention_response: WebMentionResponse,
        t_post: "post_models.TPost",
        microformat_data,
        approval_status: Optional[bool] = None,
    ) -> "TWebmention":
        return cls.objects.create(
            t_webmention_response=t_webmention_response,
            t_post=t_post,
            microformat_data=microformat_data,
            approval_status=approval_status,
        )

    def reset_moderation(self, *, microformat_data):
        """An existing webmention has been updated. Reset the moderation as the content has changed."""
        self.approval_status = None
        self.microformat_data = microformat_data
        self.save()
