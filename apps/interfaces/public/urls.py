from django.urls import include, path

urlpatterns = [
    path("", include("interfaces.public.feeds.urls", namespace="feeds")),
]


# Public urls are last so "slug-like" urls in plugins are not matched to the stream-list view.
urlpatterns.append(
    path("", include("public.urls", namespace="public")),
)
