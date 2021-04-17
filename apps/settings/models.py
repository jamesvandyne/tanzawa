from core.models import TimestampModel
from django.db import models


class MSiteSettings(TimestampModel):

    title = models.CharField(max_length=128, default="Tanzawa", blank=True)
    subtitle = models.CharField(max_length=128, default="", blank=True)
