from django.db.models import TextChoices


class WeightUnitChoices(TextChoices):
    KILOGRAMS = "kg", "Kilograms"
    POUNDS = "lbs", "Pounds"


class MoodChoices(TextChoices):
    POSITIVE = "positive", "Positive"
    NEUTRAL = "neutral", "Neutral"
    NEGATIVE = "negative", "Negative"
