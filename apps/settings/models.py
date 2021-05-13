from core.models import TimestampModel
from django.db import models


class MSiteSettings(TimestampModel):

    title = models.CharField(max_length=128, default="Tanzawa", blank=True)
    subtitle = models.CharField(max_length=128, default="", blank=True)

    footer_snippet = models.TextField(
        blank=True,
        default='<span class="help-text">Powered by <a href="http://tanzawa.blog"><span class="mr-1">🏔</span>Tanzawa</a></span>',
        help_text="Add an html snippet that will appear in the footer of your site.",
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
