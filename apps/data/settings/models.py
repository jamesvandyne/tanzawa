from django.db import models

from core.models import TimestampModel


class MSiteSettings(TimestampModel):
    title = models.CharField(max_length=128, default="Tanzawa", blank=True)
    subtitle = models.CharField(max_length=128, default="", blank=True)
    theme = models.CharField(max_length=128, default="", blank=True)
    icon = models.CharField(max_length=2, blank=True, default="🏔")
    footer_snippet = models.TextField(
        blank=True,
        default=(
            '<div class="text-center">'
            '<span class="help-text">Powered by <a href="http://tanzawa.blog">'
            '<span class="mr-1">🏔</span>Tanzawa</a></span>'
            "</div>"
        ),
        help_text="Add an html snippet that will appear in the footer of your site.",
    )
    active_trip = models.ForeignKey(
        "trips.TTrip",
        blank=True,
        null=True,
        help_text="Prefills the selected trip when creating a new post.",
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
