from collections.abc import Iterable

from django.contrib.gis.geos import Point
from django.db.models import F

from core import constants
from data.entry import models as entry_models
from data.trips import models as trip_models


def get_public_trips_for_user(user_id: int | None):
    """
    Get all publicly visible trips for a user.
    """
    return (
        trip_models.TTrip.objects.visible_for_user(user_id)
        .exclude(visibility=constants.Visibility.UNLISTED)
        .prefetch_related("t_trip_location")
        .order_by("-d_start")
    )


def get_points_for_trips(trips: Iterable[trip_models.TTrip]) -> dict[int, list[Point]]:
    """
    Get all publicly visible Points for the passed in trips.

    The results are grouped by trip.id.
    """

    # Get all points associated with publicly visible posts.
    locations = (
        entry_models.TLocation.objects.filter(t_entry__t_post__trips__in=trips)
        .exclude(t_entry__t_post__visibility=constants.Visibility.UNLISTED)
        .annotate(trip_id=F("t_entry__t_post__trips__pk"))
        .values_list("trip_id", "point")
    )
    t_location_points: dict[int, list[Point]] = {}
    # Group points by trip
    for trip_id, point in locations:
        points = t_location_points.get(trip_id, [])
        points.append(point)
        t_location_points[trip_id] = points
    return t_location_points
