from django.urls import path

from . import views

app_name = "public"

urlpatterns = [
    path("", views.home, name="home"),
    path("<uuid:uuid>", views.status_detail, name="post_detail"),
    path("author/<str:username>/", views.author, name="author"),
]
