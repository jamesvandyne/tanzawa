import datetime

from django import http
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from meta.views import Meta

from tanzawa_plugin.exercise.data.exercise import constants
from tanzawa_plugin.exercise.data.exercise import models as exercise_models
from tanzawa_plugin.exercise.domain.exercise import queries

from . import serializers


class RunsTop(generic.TemplateView):
    template_name = "exercise/public/runs.html"
    activity_types = [constants.ActivityTypeChoices.run]

    def setup(self, request, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.start_year = 2011

    def get_context_data(self, **kwargs) -> dict:
        object_list = []
        for year in range(timezone.now().date().year, self.start_year - 1, -1):
            start_at = timezone.make_aware(datetime.datetime(year=year, month=1, day=1))
            end_at = timezone.make_aware(datetime.datetime(year=year, month=12, day=31, hour=23, minute=59, second=59))
            serializer = serializers.RunsTop(
                data={},
                start_at=start_at,
                end_at=end_at,
            )
            serializer.is_valid(raise_exception=True)
            object_list.append(serializer.data)

        return super().get_context_data(
            title="Runs",
            object_list=object_list,
            nav="runs",
            meta=self._get_meta(),
        )

    def _get_meta(self) -> Meta:
        media = self._get_image_meta()
        return Meta(
            og_title="My Runs",
            description="A collection of every run I've ever made.",
            image_object=media,
            image=media["secure_url"] if media else None,
        )

    def _get_image_meta(self) -> dict[str, str | int] | None:
        last_activity = (
            exercise_models.Activity.objects.filter(activity_type__in=self.activity_types)
            .order_by("-started_at")
            .first()
        )

        if last_activity:
            return {
                "url": self.request.build_absolute_uri(
                    reverse("plugin_exercise:activity_route", args=[last_activity.pk])
                ),
                "secure_url": self.request.build_absolute_uri(
                    reverse("plugin_exercise:activity_route", args=[last_activity.pk])
                ),
                "type": "image/png",
                "width": 1000,
                "height": 1000,
                "alt": "The route of my latest run.",
            }
        return None


class RouteRaster(generic.View):
    activity: exercise_models.Activity

    def setup(self, request, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.activity = get_object_or_404(exercise_models.Activity, pk=kwargs["pk"])

    def get(self, *args, **kwargs):
        png = queries.get_png_of_route(activity=self.activity)
        return http.HttpResponse(png.read(), headers={"Content-Type": "image/png"})
