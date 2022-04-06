from django.urls import path

from . import views

urlpatterns = [
    path("<slug:stream_slug>/", views.StreamView.as_view(), name="stream"),
]
