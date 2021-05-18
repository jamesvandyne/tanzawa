from django.urls import path

from . import views

app_name = "settings"

urlpatterns = [
    path("setup", views.FirstRun.as_view(), name="first_run"),
]
