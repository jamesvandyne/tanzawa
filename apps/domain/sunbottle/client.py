import requests
from django.conf import settings


class SunbottleClientError(Exception):
    pass


class SunbottleClient:
    """
    A client for interacting with Strava.
    """

    auth_token: str

    def __init__(self, auth_token: str | None = None) -> None:
        super().__init__()
        self.auth_token = auth_token or ""

    def get_generation(self) -> list[dict]:
        summary_url = f"{settings.SUNBOTTLE_API_URL}generation_summary"
        response = requests.get(summary_url, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()
        raise SunbottleClientError(response.json())

    def _get_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.auth_token}"}


def get_client(auth_token: str | None = None) -> SunbottleClient:
    return SunbottleClient(auth_token=auth_token)
