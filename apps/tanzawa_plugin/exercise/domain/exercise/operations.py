import datetime
from dataclasses import dataclass

from django.contrib.gis import geos
from django.db import transaction

from tanzawa_plugin.exercise.data.exercise import constants, models


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
    # TODO: Record Map record if it exists

    return new_activity
