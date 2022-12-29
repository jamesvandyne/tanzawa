from django import http
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from tanzawa_plugin.exercise.application import strava
from tanzawa_plugin.exercise.data.exercise import models as exercise_models
from tanzawa_plugin.exercise.data.strava import models as strava_models
from tanzawa_plugin.exercise.domain.strava import queries as strava_queries


class ExerciseTop(generic.TemplateView):
    template_name = "exercise/exercise.html"

    def get_context_data(self, **kwargs) -> dict:
        return super().get_context_data(
            is_strava_environment_setup=strava_queries.is_strava_environment_setup(),
            user_connected_to_strava=strava_queries.is_user_connected_to_strava(self.request.user),
            activities=exercise_models.Activity.objects.all().order_by("-started_at"),
            page_title="Exercise",
            nav="exercise",
        )


class ImportActivities(generic.View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.athlete = get_object_or_404(strava_models.Athlete, user=request.user)

    def post(self, *args, **kwargs):
        try:
            strava.import_activities(self.athlete)
        except strava.UnableToImportActivities as e:
            messages.error(self.request, f"Unable to import activities {e}")
        else:
            messages.success(self.request, "Imported activities")
        return http.HttpResponseRedirect(reverse("plugin_exercise_admin:exercise"))
