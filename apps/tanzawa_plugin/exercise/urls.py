from typing import Any

from django.urls import path

from .interfaces import public

app_name = "plugin_exercise"

urlpatterns: list[Any] = [
    path("runs/", public.RunsTop.as_view(), name="runs_top"),
    path("activities/<int:pk>/route.png", public.RouteRaster.as_view(), name="activity_route"),
]
