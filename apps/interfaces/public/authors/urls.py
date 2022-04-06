from django.urls import path

from . import views

urlpatterns = [
    path("author/<str:username>/", views.AuthorDetail.as_view(), name="author"),
]
