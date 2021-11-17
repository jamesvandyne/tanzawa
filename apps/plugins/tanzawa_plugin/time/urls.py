from django.urls import path

from . import views

app_name = "plugin_time"

urlpatterns = [
    path("timezone/", views.timezone, name="timezone"),
]
