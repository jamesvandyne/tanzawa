from django.urls import path

from . import views

app_name = "indieweb"

urlpatterns = [
    # path("micropub/", views.micropub, name="micropub"),
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
]
