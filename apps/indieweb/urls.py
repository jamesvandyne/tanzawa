from django.urls import path

from . import views

app_name = "indieweb"

urlpatterns = [
    path("micropub/", views.micropub, name="micropub"),
    path(
        "webmentions/<int:pk>/approve",
        views.review_webmention,
        name="webmention_approve",
        kwargs={"approval": True},
    ),
    path(
        "webmentions/<int:pk>/disapprove",
        views.review_webmention,
        name="webmention_disapprove",
        kwargs={"approval": False},
    ),
    path(
        "indieauth/authorize",
        views.indieauth_authorize,
        name="indieauth_authorize",
    ),
    path(
        "indieauth/authorize_request",
        views.indieauth_authorize_request,
        name="indieauth_authorize_request",
    ),
    path("indieauth/token", views.token_endpoint, name="indieauth_token"),
]
