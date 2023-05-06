from django.urls import path

from . import views

app_name = "plugin_health_admin"

urlpatterns = [
    path("daily_health/", views.AddDailyHealth.as_view(), name="add_daily_health"),
    path("graph_api/", views.graph_api, name="graph_api"),
    path("", views.Health.as_view(), name="health"),
]
