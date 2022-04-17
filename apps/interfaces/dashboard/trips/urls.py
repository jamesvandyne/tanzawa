from django.urls import path
from interfaces.dashboard.trips import views

urlpatterns = [
    path("trips/", views.TripListView.as_view(), name="trips"),
    path("trips/create/", views.CreateTripView.as_view(), name="trip_create"),
    path("trips/<int:pk>/edit/", views.UpdateTripView.as_view(), name="trip_edit"),
    path("trips/<int:pk>/delete/", views.DeleteTripView.as_view(), name="trip_delete"),
]
