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
        instance.update_microformat_data()
        return instance

    def update_microformat_data(self):
        # make sure that we encode emoji and such properly
        if isinstance(self.t_webmention_response.response_body, bytes):
            cleaned_response = self.t_webmention_response.response_body.decode()
        else:
            cleaned_response = self.t_webmention_response.response_body
        parsed = mf2py.parse(doc=cleaned_response)
        mf_data = interpret_comment(
            parsed,
            self.t_webmention_response.source,
            [self.t_webmention_response.response_to],
        )
        self.microformat_data = mf_data

    def __str__(self):
        return f"{self.t_post} {self.t_webmention_response}"


class TWebmentionSend(TimestampModel):
    t_post = models.ForeignKey(
        "post.TPost", related_name="ref_t_webmention_send", on_delete=models.CASCADE
    )
    target = models.URLField()
    dt_sent = models.DateTimeField()
    success = models.BooleanField()

    class Meta:
        db_table = "t_webmention_send"
        unique_together = ("target", "t_post")

    def __str__(self):
        return self.target
