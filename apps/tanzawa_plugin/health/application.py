import datetime
from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.utils import timezone

from . import constants, models


@transaction.atomic
def save_daily_health(
    *,
    weight: Decimal,
    unit: constants.WeightUnitChoices,
    mood: constants.MoodChoices,
    measured_at: Optional[datetime.datetime] = None
) -> None:
    """
    Record daily health records.
    """
    measured_at = measured_at or timezone.now()

    models.Weight.objects.create(measurement=weight, unit=unit, measured_at=measured_at)
    models.Mood.objects.create(measurement=mood, measured_at=measured_at)
