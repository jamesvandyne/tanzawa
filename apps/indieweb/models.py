import mf2py
from core.models import TimestampModel
from django.db import models
from picklefield import PickledObjectField
from post.models import TPost
from webmention.models import WebMentionResponse

from .utils import interpret_comment


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
        # make sure that we encode emoji and such properly
        if isinstance(mention.response_body, bytes):
            cleaned_response = mention.response_body.decode()
        else:
            cleaned_response = mention.response_body
        parsed = mf2py.parse(doc=cleaned_response)
        mf_data = interpret_comment(parsed, mention.source, [mention.response_to])
        instance.microformat_data = mf_data
        return instance
