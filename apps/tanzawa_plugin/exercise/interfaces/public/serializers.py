import datetime

from django.utils.safestring import mark_safe
from rest_framework import serializers

import tanzawa_plugin.exercise.domain.exercise.operations
from tanzawa_plugin.exercise.data.exercise import constants, models
from tanzawa_plugin.exercise.domain.exercise import queries


class ActivitySerializer(serializers.Serializer):
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

    def get_year(self, obj) -> int:
        return self.start_at.year

    def get_number_of_runs(self, obj) -> int:
        return queries.number_of_activities(self.start_at, self.end_at, self.activity_types)

    def get_total_kms(self, obj) -> float:
        return queries.total_kms_for_range(self.start_at, self.end_at, self.activity_types)

    def get_total_time(self, obj) -> float:
        return (queries.total_elapsed_time(self.start_at, self.end_at, self.activity_types) / 60) / 60

    def get_activities(self, obj) -> ActivitySerializer:
        activities = (
            queries.get_activties(self.start_at, self.end_at, self.activity_types)
            .select_related("map")
            .order_by("-started_at")
        )
        return ActivitySerializer(instance=activities, many=True).data
