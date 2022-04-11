from django.urls import path

from . import views

urlpatterns = [
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
        "indieauth/authorize_request",
        views.indieauth_authorize_request,
        name="indieauth_authorize_request",
    ),
    path(
        "indieauth/authorize",
        views.indieauth_authorize,
        name="indieauth_authorize",
    ),
]
