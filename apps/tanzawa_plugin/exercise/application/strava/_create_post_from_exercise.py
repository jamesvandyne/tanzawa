import mimetypes
import pathlib
import uuid

import arrow
import requests
from django.core.files import uploadedfile
from django.db import transaction

from data.entry import models as entry_models
from data.files import models as file_models
from data.indieweb.constants import MPostKinds, MPostStatuses
from data.post import models as post_models
from domain.entry import operations as entry_ops
from domain.post import queries as post_queries
from tanzawa_plugin.exercise.data.exercise import models as exercise_models
from tanzawa_plugin.exercise.data.strava import models as strava_models
from tanzawa_plugin.exercise.domain.strava import client as strava_client
from tanzawa_plugin.exercise.domain.strava import operations as strava_ops
from tanzawa_plugin.exercise.domain.strava import queries as strava_queries


class UnableToCreatePostFromActivity(Exception):
    pass


@transaction.atomic
def create_post_from_activity(
    athlete: strava_models.Athlete, activity: exercise_models.Activity
) -> entry_models.TEntry:
    """
    Create a post for the activity.
    """
    auth_token = _determine_auth_token(athlete)
    client = strava_client.get_client(auth_token=auth_token)
    try:
        activity_detail = client.get_activity(activity.vendor_id)
    except strava_client.StravaClientError as e:
        raise UnableToCreatePostFromActivity(e)
    else:
        return _create_post_from_activity(athlete, activity, activity_detail)


def _determine_auth_token(athlete: strava_models.Athlete) -> str:
    if athlete.access_token.is_expired:
        strava_ops.refresh_token(athlete_id=athlete.pk)
        athlete.access_token.refresh_from_db()
    return athlete.access_token.token


def _create_post_from_activity(
    athlete: strava_models.Athlete, activity: exercise_models.Activity, activity_detail: dict
) -> entry_models.TEntry:
    """
    Given a Strava activity payload, publish a post for it.
    """
    status = post_queries.get_post_status(MPostStatuses.published)
    post_kind = post_queries.get_post_kind(MPostKinds.note)
    activity_time = arrow.get(activity_detail["start_date_local"], tzinfo=activity_detail["timezone"]).datetime
    if activity.entry:
        entry = entry_ops.update_entry(
            entry=activity.entry,
            status=status,
            visibility=post_models.Visibility.PUBLIC,
            updated_at=activity_time,
            e_content=_get_post_e_content(activity_detail),
            summary=_get_summary(activity_detail),
            files=None,
            published_at=activity_time,
        )
        _store_photos(activity, activity_detail)
    else:
        entry = entry_ops.create_entry(
            status=status,
            post_kind=post_kind,
            author=athlete.user,
            visibility=post_models.Visibility.PUBLIC,
            updated_at=activity_time,
            e_content=_get_post_e_content(activity_detail),
            summary=_get_summary(activity_detail),
            files=None,
            published_at=activity_time,
        )
        activity.set_entry(entry)
        _store_photos(activity, activity_detail)

    _create_syndication_link(activity, entry)
    return entry


def _get_post_e_content(activity: dict) -> str:
    return "<br/>".join([activity["name"], activity["description"]])


def _get_summary(activity: dict) -> str:
    return "\n".join([activity["name"], activity["description"]])


def _store_photos(activity: exercise_models.Activity, activity_detail: dict) -> list[exercise_models.ActivityPhoto]:
    try:
        primary_photo = activity_detail["photos"]["primary"]
        return [_get_photo(activity, primary_photo)]
    except (KeyError, TypeError):
        return []


def _get_photo(activity: exercise_models.Activity, photo: dict) -> exercise_models.ActivityPhoto:
    try:
        return exercise_models.ActivityPhoto.objects.get(vendor_id=photo["unique_id"])
    except exercise_models.ActivityPhoto.DoesNotExist:
        pass

    try:
        # Get the largest photo we can, which is 600 according to the strava example docs.
        url = photo["urls"]["600"]
    except KeyError as e:
        raise ValueError("No photo url found") from e

    upload_file = _download_photo(url)
    t_file = _store_photo(upload_file)

    return exercise_models.ActivityPhoto.objects.create(vendor_id=photo["unique_id"], activity=activity, t_file=t_file)


def _download_photo(url: str) -> uploadedfile.SimpleUploadedFile:
    response = requests.get(url)
    file_name = pathlib.Path(url).name
    content_type = response.headers.get("content-type", mimetypes.guess_type(file_name))
    upload_file = uploadedfile.SimpleUploadedFile(file_name, response.content, content_type)
    return upload_file


def _store_photo(upload_file: uploadedfile.SimpleUploadedFile):
    return file_models.TFile.objects.create(
        file=upload_file,
        uuid=uuid.uuid4(),
        filename=upload_file.name,
        mime_type=upload_file.content_type,
    )


def _create_syndication_link(activity: exercise_models.Activity, entry: entry_models.TSyndication) -> None:
    entry_models.TSyndication.objects.get_or_create(
        t_entry=entry, url=strava_queries.get_activity_url(activity.vendor_id)
    )
