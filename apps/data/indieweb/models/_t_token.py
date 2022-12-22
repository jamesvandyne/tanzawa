import binascii
import datetime
import os

from django.contrib.auth import get_user_model
from django.db import models

from core.models import TimestampModel

from ._m_micropub_scope import MMicropubScope


class TToken(TimestampModel):
    user = models.ForeignKey(get_user_model(), related_name="ref_t_token", on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=40, blank=True)
    key = models.CharField(max_length=40, blank=True)
    client_id = models.URLField()
    exchanged_at = models.DateTimeField(blank=True, null=True)

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

    @classmethod
    def new(cls, *, user, auth_token: str, client_id: str, key: str = ""):
        return cls.objects.create(
            user=user,
            auth_token=auth_token,
            key=key,
            client_id=client_id,
        )

    def set_key(self, *, key: str):
        """Set our final authorization key.
        Once key is set the initial auth token is invalid, so we clear it as well.
        """
        self.key = key
        self.auth_token = ""
        self.save()

    def set_exchanged_at(self, *, exchanged_at: datetime.datetime | None = None) -> None:
        self.exchanged_at = exchanged_at
        self.save()


class TTokenMicropubScope(TimestampModel):
    t_token = models.ForeignKey(TToken, on_delete=models.CASCADE)
    m_micropub_scope = models.ForeignKey(MMicropubScope, on_delete=models.CASCADE)

    class Meta:
        db_table = "t_token_micropub_scope"
        unique_together = ("t_token", "m_micropub_scope")
        verbose_name = "Token-Micropub Scope"

    def __str__(self):
        return f"{self.t_token}:{self.m_micropub_scope}"
