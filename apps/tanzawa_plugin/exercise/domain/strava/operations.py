import datetime

from django.contrib.auth import models as auth_models
from django.db import transaction

from tanzawa_plugin.exercise.data.strava import models

from .client import get_client


def refresh_token(athlete_id: int) -> None:
    athlete = models.Athlete.objects.get(pk=athlete_id)
    token = athlete.refresh_token.token

    client = get_client()

    token_response = client.refresh_token(refresh_token=token)

    _update_access_token(
        athlete, token_response["access_token"], datetime.datetime.fromtimestamp(token_response["expires_at"])
    )
    _update_refresh_token(athlete, token_response["refresh_token"])


@transaction.atomic
def save_short_lived_token(
    athlete_id: int, expires_at: datetime.datetime, access_token: str, refresh_token: str, user: auth_models.User
):
    athlete = _get_athlete(athlete_id, user)
    _update_access_token(athlete, access_token, expires_at)
    _update_refresh_token(athlete, refresh_token)


def _get_athlete(athlete_id: int, user: auth_models.User) -> models.Athlete:
    try:
        athlete = models.Athlete.objects.get(athlete_id=athlete_id)
    except models.Athlete.DoesNotExist:
        athlete = models.Athlete.objects.create(
            athlete_id=athlete_id,
            user=user,
        )
    return athlete


def _update_access_token(athlete: models.Athlete, token: str, expires_at: datetime.datetime) -> models.AccessToken:
    try:
        access_token = athlete.access_token
    except models.AccessToken.DoesNotExist:
        access_token = models.AccessToken.objects.create(athlete=athlete, token=token, expires_at=expires_at)
    else:
        access_token.update(token=token, expires_at=expires_at)
    return access_token


def _update_refresh_token(athlete: models.Athlete, token: str) -> models.RefreshToken:
    try:
        refresh_token = athlete.refresh_token
    except models.RefreshToken.DoesNotExist:
        refresh_token = models.RefreshToken.objects.create(
            athlete=athlete,
            token=token,
        )
    else:
        refresh_token.update(
            token=token,
        )
    return refresh_token
