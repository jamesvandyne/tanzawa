from django.db.models import TextChoices


class WeightUnitChoices(TextChoices):
    KILOGRAMS = "kg", "Kilograms"
    POUNDS = "lbs", "Pounds"


class MoodChoices(TextChoices):
    POSITIVE = "positive", "Positive"
    NEUTRAL = "neutral", "Neutral"
    NEGATIVE = "negative", "Negative"


class EmojiMoodChoices(TextChoices):
    POSITIVE = "positive", "😀"
    NEUTRAL = "neutral", "😐"
    NEGATIVE = "negative", "☹️"


class GraphDuration(TextChoices):
    SIX_WEEKS = "SIX_WEEKS", "Six Weeks"
    MONTH_TO_DATE = "MONTH_TO_DATE", "Month to date"
    LAST_MONTH = "LAST_MONTH", "Last Month"
    ALL = "ALL", "All"
