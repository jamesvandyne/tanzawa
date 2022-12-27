from django.contrib.auth import models as auth_models

from tanzawa_plugin.exercise.data.strava import models


def is_user_connected_to_strava(user: auth_models.User) -> bool:
    return models.Athlete.objects.filter(user=user).exists()
