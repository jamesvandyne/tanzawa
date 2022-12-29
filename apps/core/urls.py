from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from data.plugins import pool

from . import views

urlpatterns = [
    path("a/", include("interfaces.dashboard.urls")),
    path("webmention/", include("webmention.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("favicon.ico", views.favicon),
]

# Include any plugin urls after core urls.
plugin_urls = [path("", include(plugin_urls)) for plugin_urls in pool.plugin_pool.urls()]
urlpatterns.extend(plugin_urls)


# Public urls are last so "slug-like" urls in plugins are not matched to the stream-list view.
urlpatterns.append(
    path("", include("interfaces.public.urls", namespace="public")),
)


handler404 = views.handle404

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
