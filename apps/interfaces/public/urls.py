from django.urls import include, path

app_name = "public"

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
        "",
        include(
            "interfaces.public.files.urls",
        ),
    ),
    path("", include("interfaces.public.streams.urls")),
]
