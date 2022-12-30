import datetime

from django.contrib.gis import geos
from django.db import transaction

from tanzawa_plugin.exercise.data.strava import models as strava_models
from tanzawa_plugin.exercise.domain.exercise import operations as exercise_ops
from tanzawa_plugin.exercise.domain.exercise import queries as exercise_queries
from tanzawa_plugin.exercise.domain.strava import client as strava_client
from tanzawa_plugin.exercise.domain.strava import operations as strava_ops


class UnableToImportActivities(Exception):
    pass


@transaction.atomic
def import_activities(athlete: strava_models.Athlete) -> None:
    """
    Download the latest activities from Strava and record them to the database.
    """
    auth_token = _determine_auth_token(athlete)
    client = strava_client.get_client(auth_token=auth_token)
    try:
        activities = client.get_activities()
    except strava_client.StravaClientError as e:
        raise UnableToImportActivities(e)
    else:
        _import_activities(activities)


@transaction.atomic
def import_all_activities(athlete: strava_models.Athlete) -> None:
    """
    Download all activities from Strava and record them to the database.
    """
    auth_token = _determine_auth_token(athlete)
    client = strava_client.get_client(auth_token=auth_token)
    page = 1
    while True:
        try:
            activities = client.get_activities(page=page)
        except strava_client.StravaClientError as e:
            raise UnableToImportActivities(e)
        if activities:
            # Import all activities from this page and increase the counter, so we can load the next
            _import_activities(activities)
            page += 1
        else:
            # No more pages to load
            break


def _import_activities(activities: list[dict]) -> None:
    for strava_activity in activities:
        activity = _strava_activity_to_activity(strava_activity)
        if act := exercise_queries.get_activity_by_vendor_id(activity.vendor_id):
            exercise_ops.update_activity(act, activity)
        else:
            exercise_ops.record_activity(activity)


def _determine_auth_token(athlete: strava_models.Athlete) -> str:
    if athlete.access_token.is_expired:
        strava_ops.refresh_token(athlete_id=athlete.pk)
        athlete.access_token.refresh_from_db()
    return athlete.access_token.token


def _strava_activity_to_activity(strava_activity: dict) -> exercise_ops.Activity:
    strava_activity_map = None
    if activity_map := strava_activity.get("map"):
        strava_activity_map = exercise_ops.Map(
            vendor_id=activity_map["id"], summary_polyline=activity_map["summary_polyline"]
        )
    return exercise_ops.Activity(
        name=strava_activity["name"],
        vendor_id=strava_activity["id"],
        upload_id=strava_activity["upload_id_str"],
        distance=strava_activity["distance"],
        moving_time=strava_activity["moving_time"],
        elapsed_time=strava_activity["elapsed_time"],
        total_elevation_gain=strava_activity["total_elevation_gain"],
        elevation_high=strava_activity["elev_high"],
        elevation_low=strava_activity["elev_low"],
        activity_type=strava_activity["sport_type"],
        started_at=datetime.datetime.fromisoformat(strava_activity["start_date"]),
        # Point arguments are defined in x,y order, i.e. longitude / latitude
        start_point=geos.Point(strava_activity["start_latlng"][1], strava_activity["start_latlng"][0]),
        end_point=geos.Point(strava_activity["end_latlng"][1], strava_activity["end_latlng"][0]),
        activity_map=strava_activity_map,
        average_speed=strava_activity["average_speed"],
        max_speed=strava_activity["max_speed"],
        average_heartrate=strava_activity.get("average_heartrate"),
        max_heartrate=strava_activity.get("max_heartrate"),
    )
