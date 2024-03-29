from django.urls import path

from interfaces.public.feeds import views

urlpatterns = [
    path("feed/", views.AllEntriesFeed(), name="feed"),
    path("<slug:stream_slug>/feed/", views.StreamFeed(), name="stream_feed"),
]
