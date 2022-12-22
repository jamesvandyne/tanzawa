from django.urls import path

from . import views

urlpatterns = [
    path("blog/", views.BlogListView.as_view(), name="blog"),
    path("", views.HomeView.as_view(), name="home"),
]
