from django.urls import path

from . import views

urlpatterns = [
    path("maps/cluster", views.cluster_map, name="cluster_map"),
]
