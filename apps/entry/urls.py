from django.urls import path
from indieweb.constants import MPostKinds

from . import views

urlpatterns = [
    path("article/create/", views.article_create, name="article_create"),
    path("article/<int:pk>/edit/", views.article_edit, name="article_edit"),
    path("article/<int:pk>/delete/", views.status_delete, name="article_delete"),

    path("status/create/", views.status_create, name="status_create"),
    path("status/<int:pk>/", views.status_detail, name="status_detail"),
    path("status/<int:pk>/edit/", views.status_edit, name="status_edit"),
    path("status/<int:pk>/delete/", views.status_delete, name="status_delete"),
    path(
        "status/",
        views.TEntryListView.as_view(m_post_kind_key=MPostKinds.note),
        name="status_list",
    ),
]
