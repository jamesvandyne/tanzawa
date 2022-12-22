from django.urls import include, path

from data.plugins import pool

app_name = "public"

plugin_urls = [path("", include(plugin_urls)) for plugin_urls in pool.plugin_pool.urls()]


urlpatterns = [
    path("", include("interfaces.public.feeds.urls")),
    path(
        "",
        include(
            "interfaces.public.home.urls",
        ),
    ),
    path("", include("interfaces.public.entry.urls")),
    path("", include("interfaces.public.authors.urls")),
    path(
        "",
        include(
            "interfaces.public.search.urls",
        ),
    ),
    path(
        "",
        include(
            "interfaces.public.trips.urls",
        ),
    ),
    path(
        "",
        include(
            "interfaces.public.maps.urls",
        ),
    ),
    path(
        "files/",
        include(
            "interfaces.public.files.urls",
        ),
    ),
    path(
        "",
        include("interfaces.public.indieweb.urls"),
    ),
    *plugin_urls,
    path("", include("interfaces.public.streams.urls")),
]
