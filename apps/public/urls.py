from django.urls import path

from . import views

app_name = "public"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("<uuid:uuid>", views.status_detail, name="post_detail"),
    path("author/<str:username>/", views.AuthorDetail.as_view(), name="author"),
    path("<slug:stream_slug>/", views.StreamView.as_view(), name="stream"),
]
