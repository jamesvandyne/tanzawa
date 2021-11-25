from django.urls import path

from . import views

app_name = "plugin_now_admin"

urlpatterns = [
    path("edit/", views.UpdateNowAdmin.as_view(), name="update_now"),
]
