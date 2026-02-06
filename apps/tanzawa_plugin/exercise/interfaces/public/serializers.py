import datetime

from django.db.models import Sum
from django.utils.safestring import mark_safe
from rest_framework import serializers

import tanzawa_plugin.exercise.domain.exercise.operations
from tanzawa_plugin.exercise.data.exercise import constants, models
from tanzawa_plugin.exercise.domain.exercise import queries


class _RunsTopActivity(serializers.Serializer):
    route_svg = serializers.SerializerMethodField()

    def get_route_svg(self, obj: models.Activity) -> str:
        return mark_safe(tanzawa_plugin.exercise.domain.exercise.operations.maybe_create_and_get_svg(obj, 128, 128))


class RunsTop(serializers.Serializer):
    start_at: datetime.datetime
    end_at: datetime.datetime
    activity_types = [constants.ActivityTypeChoices.run]

    year = serializers.SerializerMethodField()
    number_of_runs = serializers.SerializerMethodField()
    total_kms = serializers.SerializerMethodField()
    total_time = serializers.SerializerMethodField()
    activities = serializers.SerializerMethodField()

    def __init__(self, *args, start_at: datetime.datetime, end_at: datetime.datetime, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.start_at = start_at
        self.end_at = end_at
        self._activities = (
            queries.get_activties(self.start_at, self.end_at, self.activity_types)
            .select_related("map")
            .order_by("-started_at")
        )
        self._year_stats = self._activities.aggregate(total_distance=Sum("distance"), total_time=Sum("elapsed_time"))

    def get_year(self, obj) -> int:
        return self.start_at.year

    def get_number_of_runs(self, obj) -> int:
        return len(self._activities)

    def get_total_kms(self, obj) -> float:
        return (self._year_stats["total_distance"] or 0) / 1000

    def get_total_time(self, obj) -> float:
        return (self._year_stats["total_time"] or 0 / 60) / 60

    def get_activities(self, obj) -> _RunsTopActivity:
        return _RunsTopActivity(instance=self._activities, many=True).data


class ActivityPhoto(serializers.Serializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj: models.ActivityPhoto) -> str:
        return obj.t_file.get_absolute_url()


class Activity(serializers.Serializer):
    distance_km = serializers.SerializerMethodField()
    elapsed_time_minutes = serializers.SerializerMethodField()
    average_heartrate = serializers.SerializerMethodField()
    total_elevation_gain = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    route_svg = serializers.SerializerMethodField()

    def get_distance_km(self, obj: models.Activity) -> float:
        return obj.distance_km

    def get_elapsed_time_minutes(self, obj: models.Activity) -> float:
        return obj.elapsed_time_minutes

    def get_average_heartrate(self, obj: models.Activity) -> float:
        return obj.average_heartrate

    def get_total_elevation_gain(self, obj: models.Activity) -> float:
        return obj.total_elevation_gain

    def get_photos(self, obj: models.Activity) -> dict:
        return ActivityPhoto(obj.photos, many=True).data

    def get_route_svg(self, obj: models.Activity) -> str:
        return mark_safe(
            tanzawa_plugin.exercise.domain.exercise.operations.maybe_create_and_get_svg(obj, 256, 256, css_class="h-80")
        )
