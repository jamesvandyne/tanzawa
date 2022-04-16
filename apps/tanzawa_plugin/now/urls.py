from django.urls import path

from . import views

app_name = "plugin_now"

urlpatterns = [
    path("now/", views.PublicViewNow.as_view(), name="now"),
]
