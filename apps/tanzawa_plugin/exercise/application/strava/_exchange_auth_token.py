import datetime

from django.contrib.auth import models as auth_models
from django.db import transaction

from tanzawa_plugin.exercise.domain.strava import client as strava_client
from tanzawa_plugin.exercise.domain.strava import operations as strava_ops


@transaction.atomic
def exchange_auth_code(*, authorization_code: str, user: auth_models.User) -> None:
    """
    Save an auth token for a given athlete.
    """

    client = strava_client.get_client()

    token_response = client.get_short_lived_token(authorization_code=authorization_code)
    strava_ops.save_short_lived_token(
        athlete_id=token_response["athlete"]["id"],
        expires_at=datetime.datetime.fromtimestamp(token_response["expires_at"]),
        access_token=token_response["access_token"],
        refresh_token=token_response["refresh_token"],
        user=user,
    )
