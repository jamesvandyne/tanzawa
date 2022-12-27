import datetime

from django.db.models import Sum

from tanzawa_plugin.exercise.data.exercise import models


def get_activity_by_vendor_id(vendor_id: str) -> models.Activity | None:
    try:
        return models.Activity.objects.get(vendor_id=vendor_id)
    except models.Activity.DoesNotExist:
        return None


def number_of_activities(
    start: datetime.datetime | None = None,
    end: datetime.datetime | None = None,
    activity_types: list[models.constants.ActivityTypeChoices] | None = None,
) -> int:
    qs = models.Activity.objects.all()
    if start and end:
        qs = qs.filter(started_at__range=(start, end))
    if activity_types:
        qs = qs.filter(activity_type__in=activity_types)
    return qs.count()


def total_kms_for_range(
    start: datetime.datetime | None = None,
    end: datetime.datetime | None = None,
    activity_types: list[models.constants.ActivityTypeChoices] | None = None,
) -> float:
    qs = models.Activity.objects.all()
    if start and end:
        qs = qs.filter(started_at__range=(start, end))
    if activity_types:
        qs = qs.filter(activity_type__in=activity_types)
    return qs.aggregate(total_distance=Sum("distance"))["total_distance"] / 1000


def total_elapsed_time(
    start: datetime.datetime | None = None,
    end: datetime.datetime | None = None,
    activity_types: list[models.constants.ActivityTypeChoices] | None = None,
) -> int:
    qs = models.Activity.objects.all()
    if start and end:
        qs = qs.filter(started_at__range=(start, end))
    if activity_types:
        qs = qs.filter(activity_type__in=activity_types)
    return qs.aggregate(total_elapsed_time=Sum("elapsed_time"))["total_elapsed_time"]
