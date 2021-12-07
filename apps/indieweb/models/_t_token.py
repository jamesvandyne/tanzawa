import binascii
import os

from core.models import TimestampModel
from django.contrib.auth import get_user_model
from django.db import models

from ._m_micropub_scope import MMicropubScope


class TToken(TimestampModel):
    user = models.ForeignKey(get_user_model(), related_name="ref_t_token", on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=40, blank=True)
    key = models.CharField(max_length=40, blank=True)
    client_id = models.URLField()

    micropub_scope = models.ManyToManyField(
        MMicropubScope,
        through="TTokenMicropubScope",
        through_fields=("t_token", "m_micropub_scope"),
    )

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    class Meta:
        db_table = "t_token"
        verbose_name = "Token"
        verbose_name_plural = "Tokens"

    def __str__(self):
        return f"{self.auth_token}::{self.key}"


class TTokenMicropubScope(TimestampModel):
    t_token = models.ForeignKey(TToken, on_delete=models.CASCADE)
    m_micropub_scope = models.ForeignKey(MMicropubScope, on_delete=models.CASCADE)

    class Meta:
        db_table = "t_token_micropub_scope"
        unique_together = ("t_token", "m_micropub_scope")
        verbose_name = "Token-Micropub Scope"

    def __str__(self):
        return f"{self.t_token}:{self.m_micropub_scope}"
