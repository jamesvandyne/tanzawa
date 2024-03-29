from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic

from tanzawa_plugin.exercise.application import strava
from tanzawa_plugin.exercise.data.exercise import models as exercise_models
from tanzawa_plugin.exercise.data.strava import models as strava_models
from tanzawa_plugin.exercise.domain.exercise import queries as exercise_queries
from tanzawa_plugin.exercise.domain.strava import queries as strava_queries


@method_decorator(login_required, name="dispatch")
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


@method_decorator(login_required, name="dispatch")
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


@method_decorator(login_required, name="dispatch")
class ActivityDetail(generic.TemplateView):
    template_name = "exercise/activity/detail.html"
    activity: exercise_models.Activity

    def setup(self, request, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.activity = get_object_or_404(exercise_models.Activity, pk=kwargs["pk"])

    def get_context_data(self, **kwargs) -> dict:
        return super().get_context_data(
            activity=self.activity,
            default_lat=self.activity.start_point.y,
            default_lon=self.activity.start_point.x,
            point_list=exercise_queries.get_point_list(self.activity),
        )


@method_decorator(login_required, name="dispatch")
class CreatePostFromActivity(generic.View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.athlete = get_object_or_404(strava_models.Athlete, user=request.user)
        self.activity = get_object_or_404(exercise_models.Activity, pk=kwargs["pk"])

    def post(self, *args, **kwargs):
        try:
            entry = strava.create_post_from_activity(athlete=self.athlete, activity=self.activity)
        except strava.UnableToCreatePostFromActivity as e:
            messages.error(self.request, f"Unable to create post from activity {e}")
        else:
            messages.success(self.request, "Created entry from activity")
            return http.HttpResponseRedirect(reverse("status_edit", args=[entry.pk]))

        return http.HttpResponseRedirect(reverse("plugin_exercise_admin:exercise"))
