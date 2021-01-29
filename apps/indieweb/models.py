import mf2py
import mf2util
from core.models import TimestampModel
from django.db import models
from picklefield import PickledObjectField
from post.models import TPost
from webmention.models import WebMentionResponse


class TWebmention(TimestampModel):

    t_webmention_response = models.ForeignKey(
        WebMentionResponse, related_name="ref_t_webmention", on_delete=models.CASCADE
    )
    t_post = models.ForeignKey(
        "post.TPost", related_name="ref_t_webmention", on_delete=models.CASCADE
    )
    approval_status = models.BooleanField(null=True, blank=True)
    microformat_data = PickledObjectField()

    class Meta:
        db_table = "t_webmention"
        unique_together = ("t_webmention_response", "t_post")

    @classmethod
    def instance_from_webmentionresponse(
        cls, mention: WebMentionResponse, t_post: TPost
    ) -> "TWebmention":
        instance = cls(t_webmention_response=mention, t_post=t_post)
        parsed = mf2py.parse(doc=mention.response_body)
        mf_data = mf2util.interpret_comment(
            parsed, mention.source, [mention.response_to]
        )
        instance.microformat_data = mf_data

        return instance
