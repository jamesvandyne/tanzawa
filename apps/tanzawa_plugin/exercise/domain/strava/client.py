import requests
from django.conf import settings

from tanzawa_plugin.exercise.data.strava import constants


class StravaClientError(Exception):
    pass


class StravaClient:
    """
    A client for interacting with Strava.
    """

    auth_token: str

    def __init__(self, auth_token: str | None = None) -> None:
        super().__init__()
        self.auth_token = auth_token or ""

    def get_activities(self, page: int = 1) -> list[dict]:
        """
        Get the activities for the authorized athlete.
        """
        run_url = f"{constants.STRAVA_ACTIVITIES_ENDPOINT}?page={page}"
        response = requests.get(run_url, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        raise StravaClientError(response.json())

    def get_activity(self, activity_id: str) -> dict:
        """
        Get the details for a given activity.
        """
        activity_url = constants.STRAVA_ACTIVITY_DETAIL_ENDPOINT.format(id=activity_id)
        response = requests.get(activity_url, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        raise StravaClientError(response.json())

    def _get_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.auth_token}"}

    def refresh_token(self, refresh_token: str) -> dict:
        """
        Get refresh token.
        """
        payload = {
            "client_id": settings.STRAVA_CLIENT_ID,
            "client_secret": settings.STRAVA_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(constants.STRAVA_OAUTH_TOKEN_URL, data=payload)
        if response.status_code == 200:
            return response.json()
        raise StravaClientError(response.json())

    def get_short_lived_token(self, authorization_code: str) -> dict:
        """
        Get an auth token that can be used for making requests.
        """
        payload = {
            "client_id": settings.STRAVA_CLIENT_ID,
            "client_secret": settings.STRAVA_CLIENT_SECRET,
            "code": authorization_code,
            "grant_type": "authorization_code",
        }
        response = requests.post(constants.STRAVA_OAUTH_TOKEN_URL, data=payload)
        if response.status_code == 200:
            print(response.json())
            return response.json()
        raise StravaClientError(response.json())


def get_client(auth_token: str | None = None) -> StravaClient:
    return StravaClient(auth_token=auth_token)
