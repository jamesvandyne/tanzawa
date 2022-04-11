from core.models import TimestampModel
from django.db import models


class MMicropubScope(TimestampModel):

    key = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=16)

    class Meta:
        db_table = "m_micropub_scope"
        verbose_name = "Micropub Scope"
        verbose_name_plural = "Micropub Scopes"

    def __str__(self):
        return self.name

    def help_text(self):
        if self.key == "media":
            return "Allows the application to upload media"
        return f"Allows the application to {self.name.lower()} posts"
