from django.urls import path

from . import views

urlpatterns = [
    path("article/create/", views.CreateArticleView.as_view(), name="article_create"),
    path("article/<int:pk>/edit/", views.UpdateArticleView.as_view(), name="article_edit"),
    path("article/<int:pk>/delete/", views.status_delete, name="article_delete"),
    path("status/create/", views.CreateStatusView.as_view(), name="status_create"),
    path("status/<int:pk>/", views.status_detail, name="status_detail"),
    path("status/<int:pk>/edit/", views.UpdateStatusView.as_view(), name="status_edit"),
    path("status/<int:pk>/delete/", views.status_delete, name="status_delete"),
    path("reply/create/", views.CreateReplyView.as_view(), name="reply_create"),
    path("reply/<int:pk>/edit/", views.UpdateReplyView.as_view(), name="reply_edit"),
    path("reply/meta_info/", views.ExtractReplyMetaView.as_view(), name="reply_meta"),
    path("bookmark/create/", views.CreateBookmarkView.as_view(), name="bookmark_create"),
    path(
        "bookmark/<int:pk>/edit/",
        views.UpdateBookmarkView.as_view(),
        name="bookmark_edit",
    ),
    path(
        "bookmark/meta_info/",
        views.ExtractBookmarkMetaView.as_view(),
        name="bookmark_meta",
    ),
    path("checkin/<int:pk>/edit/", views.UpdateCheckinView.as_view(), name="checkin_edit"),
    path(
        "posts/",
        views.TEntryListView.as_view(),
        name="posts",
    ),
    path("posts/<int:pk>", views.edit_post, name="post_edit"),
]
