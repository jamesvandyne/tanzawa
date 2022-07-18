from core.models import TimestampModel
from django.db import models

from . import constants


class Weight(TimestampModel):
    """
    A body weight measurement.
    """

    measurement = models.DecimalField(max_digits=5, decimal_places=2)
    unit = models.CharField(
        max_length=3, choices=constants.WeightUnitChoices.choices, default=constants.WeightUnitChoices.KILOGRAMS
    )
    measured_at = models.DateTimeField(unique_for_date=True)

    class Meta:
        verbose_name = "Weight"
        verbose_name_plural = "Weight"

    def __str__(self) -> str:
        return f"Weight {self.id} {self.measurement} {self.unit}"


class Mood(TimestampModel):
    """
    A mental health measurement.
    """

    measurement = models.CharField(max_length=12, choices=constants.MoodChoices.choices)
    measured_at = models.DateTimeField(unique_for_date=True)

    class Meta:
        verbose_name = "Mood"
        verbose_name_plural = "Mood"

    def __str__(self) -> str:
        return f"Mood {self.id} {self.measurement}"

    @property
    def emoji(self):
        return constants.EmojiMoodChoices(self.measurement).label
