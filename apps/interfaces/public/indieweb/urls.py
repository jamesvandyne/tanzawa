from django.urls import path

from . import views

urlpatterns = [
    path("micropub/", views.micropub, name="micropub"),
    path("indieauth/token", views.token_endpoint, name="indieauth_token"),
]
