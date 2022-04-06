from django.urls import path

from . import views

urlpatterns = [
    path("trips/", views.TripListView.as_view(), name="trips"),
    path("trips/<uuid:uuid>", views.trip_detail, name="trip_detail"),
]
