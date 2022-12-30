from django.urls import path

from .interfaces import dashboard

app_name = "plugin_exercise_admin"

urlpatterns = [
    path(
        "",
        dashboard.ExerciseTop.as_view(),
        name="exercise",
    ),
    path(
        "activities/<int:pk>/modal/",
        dashboard.ActivityDetail.as_view(),
        name="activity_detail",
    ),
    # Import
    path(
        "activities/import",
        dashboard.ImportActivities.as_view(),
        name="import_activities",
    ),
    # Strava API
    path(
        "strava/request_authorization",
        dashboard.StravaRequestAuthorization.as_view(),
        name="strava_request_authorization",
    ),
    path(
        "strava/request_authorization/success",
        dashboard.StravaAuthorizationSuccessful.as_view(),
        name="strava_request_authorization_success",
    ),
]
