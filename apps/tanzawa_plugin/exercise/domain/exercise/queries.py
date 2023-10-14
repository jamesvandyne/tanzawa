import datetime

import polyline
from django.db.models import QuerySet, Sum

from tanzawa_plugin.exercise.data.exercise import models


def get_activity_by_vendor_id(vendor_id: str) -> models.Activity | None:
    try:
        return models.Activity.objects.get(vendor_id=vendor_id)
    except models.Activity.DoesNotExist:
        return None


def get_activties(
    start_at: datetime.datetime | None = None,
    end_at: datetime.datetime | None = None,
    activity_types: list[models.constants.ActivityTypeChoices] | None = None,
) -> QuerySet[models.Activity]:
    qs = models.Activity.objects.all()
    if start_at and end_at:
        qs = qs.filter(started_at__range=(start_at, end_at))
    if activity_types:
        qs = qs.filter(activity_type__in=activity_types)
    return qs


def number_of_activities(
    start: datetime.datetime | None = None,
    end: datetime.datetime | None = None,
    activity_types: list[models.constants.ActivityTypeChoices] | None = None,
) -> int:
    return get_activties(start, end, activity_types).count()


def total_kms_for_range(
    start: datetime.datetime | None = None,
    end: datetime.datetime | None = None,
    activity_types: list[models.constants.ActivityTypeChoices] | None = None,
) -> float:
    return (
        get_activties(start, end, activity_types).aggregate(total_distance=Sum("distance"))["total_distance"] or 0
    ) / 1000


def total_elapsed_time(
    start: datetime.datetime | None = None,
    end: datetime.datetime | None = None,
    activity_types: list[models.constants.ActivityTypeChoices] | None = None,
) -> int:
    return (
        get_activties(start, end, activity_types).aggregate(total_elapsed_time=Sum("elapsed_time"))[
            "total_elapsed_time"
        ]
        or 0
    )


def get_point_list(activity: models.Activity) -> list[list[float]]:
    """
    Return a list of points that can be used to plot a path for a given Activity.
    """
    try:
        return [list(coords) for coords in polyline.decode(activity.map.summary_polyline)]
    except models.Map.DoesNotExist:
        return []
