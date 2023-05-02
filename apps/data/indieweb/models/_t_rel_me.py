from django.contrib.auth import get_user_model
from django.db import models

from core.models import TimestampModel


class TRelMe(TimestampModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="relme")
    url = models.URLField(
        unique=True, help_text="URL to your profile on other sites. Email adddress should start with mailto."
    )
    display_name = models.CharField(max_length=64, blank=True)

    class Meta:
        db_table = "t_rel_me"
        verbose_name = "Relme"
        verbose_name_plural = "Relme"

    def __str__(self):
        return self.url
