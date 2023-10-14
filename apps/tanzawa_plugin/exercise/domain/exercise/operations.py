import datetime
import io
from dataclasses import dataclass

import cairosvg
from django.contrib.gis import geos
from django.db import transaction
from django.template.loader import render_to_string

from domain.gis import queries as gis_queries
from tanzawa_plugin.exercise.data.exercise import constants, models
from tanzawa_plugin.exercise.domain.exercise.queries import get_point_list


@dataclass
class Map:
    summary_polyline: str
    vendor_id: str | None = None


@dataclass(frozen=True)
class Activity:
    name: str
    vendor_id: str
    upload_id: str
    distance: float | None
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    elevation_high: float
    elevation_low: float
    activity_type: constants.ActivityTypeChoices
    started_at: datetime.datetime
    start_point: geos.Point
    end_point: geos.Point
    average_speed: float
    max_speed: float
    average_heartrate: float | None
    max_heartrate: float | None
    activity_map: Map | None


@transaction.atomic
def record_activity(activity: Activity) -> models.Activity:
    new_activity = models.Activity.new(
        name=activity.name,
        vendor_id=activity.vendor_id,
        upload_id=activity.upload_id,
        distance=activity.distance,
        moving_time=activity.moving_time,
        elapsed_time=activity.elapsed_time,
        total_elevation_gain=activity.total_elevation_gain,
        elevation_high=activity.elevation_high,
        elevation_low=activity.elevation_low,
        activity_type=activity.activity_type,
        started_at=activity.started_at,
        start_point=activity.start_point,
        end_point=activity.end_point,
        average_speed=activity.average_speed,
        max_speed=activity.max_speed,
        average_heartrate=activity.average_heartrate,
        max_heartrate=activity.max_heartrate,
    )
    if activity.activity_map:
        models.Map.objects.create(
            activity=new_activity,
            vendor_id=activity.activity_map.vendor_id,
            summary_polyline=activity.activity_map.summary_polyline,
        )

    return new_activity


@transaction.atomic
def update_activity(instance: models.Activity, activity: Activity) -> None:
    instance.update(
        name=activity.name,
        vendor_id=activity.vendor_id,
        upload_id=activity.upload_id,
        distance=activity.distance,
        moving_time=activity.moving_time,
        elapsed_time=activity.elapsed_time,
        total_elevation_gain=activity.total_elevation_gain,
        elevation_high=activity.elevation_high,
        elevation_low=activity.elevation_low,
        activity_type=activity.activity_type,
        started_at=activity.started_at,
        start_point=activity.start_point,
        end_point=activity.end_point,
        average_speed=activity.average_speed,
        max_speed=activity.max_speed,
        average_heartrate=activity.average_heartrate,
        max_heartrate=activity.max_heartrate,
    )
    if activity.activity_map:
        try:
            activity_map = instance.map
        except models.Map.DoesNotExist:
            models.Map.objects.create(
                activity=instance,
                vendor_id=activity.activity_map.vendor_id,
                summary_polyline=activity.activity_map.summary_polyline,
            )
        else:
            activity_map.update(
                vendor_id=activity.activity_map.vendor_id,
                summary_polyline=activity.activity_map.summary_polyline,
            )


def maybe_create_and_get_svg(
    activity: models.Activity, width: int = 1000, height: int = 1000, css_class: str = "h-32"
) -> str:
    """
    Get a svg for a given activity.
    """
    if map := activity.map:
        if map.svg:
            return map.svg.replace("h-size", css_class)
        svg_data = _get_svg(activity, width, height)
        svg = render_to_string("exercise/activity/route.svg", {"svg": svg_data, "css_class": "h-size"})
        map.set_svg(svg)
        return map.svg.replace("h-size", css_class)
    return ""


def maybe_create_and_get_png_of_route(activity: models.Activity, width: int = 1000, height: int = 1000) -> io.BytesIO:
    svg = maybe_create_and_get_svg(activity, width, height)
    png = io.BytesIO()
    cairosvg.svg2png(svg, write_to=png, output_width=width, output_height=height)
    png.seek(0)
    return png


@dataclass
class ActivitySvg:
    points: list[list[float]]
    width: int
    height: int


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
