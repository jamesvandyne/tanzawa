from django.core.management.base import BaseCommand, CommandError

from data.plugins import pool
from tanzawa_plugin.exercise.application.strava import import_all_activities
from tanzawa_plugin.exercise.data.strava import models


class Command(BaseCommand):
    help = "Download all strava activities"

    def handle(self, *args, **options):
        if "Exercise" not in [p.name for p in pool.plugin_pool.enabled_plugins()]:
            raise CommandError("Exercise plugin not enabled.")

        for athlete in models.Athlete.objects.all():
            self.stdout.write(f"Importing activities for athlete {athlete}")
            import_all_activities(athlete)
