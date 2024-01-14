from django.urls import path

from . import views

urlpatterns = [
    path("upload", views.micropub_media, name="micropub_media"),
    path("<uuid:uuid>", views.get_media, name="get_media"),
    path("<uuid:uuid>/modal", views.get_media_modal, name="get_media_modal"),
]
