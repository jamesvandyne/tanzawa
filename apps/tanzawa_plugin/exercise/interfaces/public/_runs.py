import datetime

from django.utils import timezone
from django.views import generic

from tanzawa_plugin.exercise.data.exercise import constants
from tanzawa_plugin.exercise.domain.exercise import queries


class RunsTop(generic.TemplateView):
    template_name = "exercise/public/runs.html"

    def get_context_data(self, **kwargs):
        today = timezone.now().date()
        start_date = timezone.make_aware(datetime.datetime(year=today.year, month=1, day=1))
        end_date = timezone.make_aware(
            datetime.datetime(year=today.year, month=12, day=31, hour=23, minute=59, second=59)
        )
        activity_types = [constants.ActivityTypeChoices.run]
        return super().get_context_data(
            nav="runs",
            number_of_runs=queries.number_of_activities(start_date, end_date, activity_types),
            total_kms=queries.total_kms_for_range(start_date, end_date, activity_types),
            total_time=((queries.total_elapsed_time(start_date, end_date, activity_types) / 60) / 60),
        )
