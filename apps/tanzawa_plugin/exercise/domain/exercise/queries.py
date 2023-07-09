import datetime
import functools
import io
from dataclasses import dataclass

import cairosvg
import polyline
from django.db.models import QuerySet, Sum
from django.template.loader import render_to_string

from domain.gis import queries as gis_queries
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


@dataclass
class ActivitySvg:
    points: list[list[float]]
    width: int
    height: int


@functools.lru_cache(maxsize=256)
def get_svg(activity: models.Activity, width: int = 1000, height: int = 1000, css_class: str = "h-32") -> str:
    """
    Get a svg for a given activity.
    """
    svg_data = _get_svg(activity, width, height)
    return render_to_string("exercise/activity/route.svg", {"svg": svg_data, "css_class": css_class})


def get_png_of_route(activity: models.Activity, width: int = 1000, height: int = 1000) -> io.BytesIO:
    svg = get_svg(activity, width, height)
    png = io.BytesIO()
    cairosvg.svg2png(svg, write_to=png, output_width=width, output_height=height)
    png.seek(0)
    return png


def _get_svg(activity: models.Activity, width: int = 50, height: int = 50, padding: int = 10) -> ActivitySvg | None:
    """
    Translate the geocoordinates of an activity to points that can be used when drawing a svg.
    """
    point_list = get_point_list(activity)
    if point_list:
        x_values: list[float] = []
        y_values: list[float] = []

        for lat, lon in point_list:
            # Use Mercator points so route doesn't look slightly off when flattened.
            projected_x = gis_queries.lon2x(lon)
            projected_y = gis_queries.lat2y(lat)
            x_values.append(projected_x)
            y_values.append(projected_y)

        max_x, max_y = max(x_values), max(y_values)
        min_x, min_y = min(x_values), min(y_values)
        map_width = max_x - min_x
        map_height = max_y - min_y
        center_x = (max_x + min_x) / 2
        center_y = (max_y + min_y) / 2
        scale = min(width / map_width, height / map_height)
        return ActivitySvg(
            points=[
                [(x - center_x) * scale + width / 2, (y - center_y) * scale + height / 2]
                for x, y in zip(x_values, y_values)
            ],
            width=width + padding,
            height=height + padding,
        )

    return None
