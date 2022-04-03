from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("a/", include("interfaces.dashboard.urls")),
    path("a/", include("post.urls", namespace="post")),
    path("a/", include("files.admin_urls")),
    path("a/", include("plugins.urls")),
    path("a/wordpress/", include("wordpress.urls", namespace="wordpress")),
    path("a/", include("indieweb.urls", namespace="indieweb")),
    path("files/", include("files.urls")),
    path("webmention/", include("webmention.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("favicon.ico", views.favicon),
]


# Public urls are last so "slug-like" urls in plugins are not matched to the stream-list view.
urlpatterns.append(
    path("", include("interfaces.public.urls")),
)


handler404 = views.handle404

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
