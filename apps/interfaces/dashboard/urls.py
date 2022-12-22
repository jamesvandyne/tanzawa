from django.urls import include, path
from django.utils import text

from data.plugins import pool

urlpatterns = [
    path("", include("interfaces.dashboard.entry.urls")),
    path("", include("interfaces.dashboard.trips.urls")),
    path("", include("interfaces.dashboard.files.urls")),
    path("", include("interfaces.dashboard.indieweb.urls")),
    path("", include("interfaces.dashboard.plugins.urls")),
    path("wordpress/", include("interfaces.dashboard.wordpress.urls", namespace="wordpress")),
    path("", include("interfaces.dashboard.top.urls", namespace="post")),
]


plugin_admin_urls = [
    path(f"plugins/{text.slugify(plugin.name)}/", include(plugin.admin_urls))
    for plugin in pool.plugin_pool.enabled_plugins()
    if plugin.admin_urls
]
urlpatterns.extend(plugin_admin_urls)
