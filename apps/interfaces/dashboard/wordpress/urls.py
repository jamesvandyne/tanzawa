from django.urls import path

from interfaces.dashboard.wordpress import views

app_name = "wordpress"

urlpatterns = [
    path("upload/", views.TWordpressCreate.as_view(), name="t_wordpress_create"),
    path("upload/<int:pk>/categories", views.category_mappings, name="t_category_mapping"),
    path(
        "upload/<int:pk>/postkinds",
        views.post_kind_mappings,
        name="t_post_kind_mapping",
    ),
    path(
        "upload/<int:pk>/attachments",
        views.t_wordpress_attachments,
        name="t_wordpress_attachment_list",
    ),
    path(
        "attachment/<uuid:uuid>/import",
        views.import_attachment,
        name="import_attachment",
    ),
    path(
        "upload/<int:pk>/import_posts",
        views.import_posts,
        name="import_posts",
    ),
    path("", views.TWordpressListView.as_view(), name="t_wordpress_list"),
]
