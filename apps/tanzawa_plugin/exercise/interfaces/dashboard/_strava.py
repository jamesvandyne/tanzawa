"""
API Views for interacting with Strava
"""

import logging
from urllib import parse as url_parse

from django import http
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.views import generic

from tanzawa_plugin.exercise.application.strava import exchange_auth_code
from tanzawa_plugin.exercise.data.strava import constants

logger = logging.getLogger(__name__)


# OAuth Authorization Views
class StravaRequestAuthorization(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        redirect_path = reverse("plugin_exercise_admin:strava_request_authorization_success")
        params_oauth = {
            "client_id": settings.STRAVA_CLIENT_ID,
            "response_type": "code",
            # Set this to use current url
            "redirect_uri": self.request.build_absolute_uri(redirect_path),
            "scope": "read,profile:read_all,activity:read_all",
            # Set this to use plugin url?
            "state": self.request.build_absolute_uri("plugin_exercise_admin:exercise"),
            "approval_prompt": "auto",
        }
        values_url = url_parse.urlencode(params_oauth)

        return f"{constants.STRAVA_OAUTH_AUTHORIZE_URL}?{values_url}"


class StravaAuthorizationSuccessful(generic.View):
    def get(self, *args, **kwargs):
        exchange_auth_code(authorization_code=self.request.GET["code"], user=self.request.user)
        messages.success(self.request, "Connected to Strava!")
        return http.HttpResponseRedirect(reverse("plugin_exercise_admin:exercise"))
