from django.urls import path

from . import views

app_name = "feeds"

urlpatterns = [
    path("feed/", views.AllEntriesFeed(), name="feed"),
    path("<slug:stream_slug>/feed/", views.StreamFeed(), name="stream_feed"),
]
