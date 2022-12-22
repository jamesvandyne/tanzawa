from django.urls import path

from . import views

urlpatterns = [
    path("now/", views.PublicViewNow.as_view(), name="now"),
]
