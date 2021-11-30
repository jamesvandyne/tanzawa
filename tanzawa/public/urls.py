from django.urls import path

from . import views

app_name = "public"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("<uuid:uuid>", views.status_detail, name="post_detail"),
    path("author/<str:username>/", views.AuthorDetail.as_view(), name="author"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("trips/", views.TripListView.as_view(), name="trips"),
    path("trips/<uuid:uuid>", views.trip_detail, name="trip_detail"),
    path("maps/cluster", views.cluster_map, name="cluster_map"),
    path("<slug:stream_slug>/", views.StreamView.as_view(), name="stream"),
]
