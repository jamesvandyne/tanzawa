"""web20core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from plugins.core import plugin_pool

from . import views

urlpatterns = [
    path("a/", include("entry.urls")),
    path("a/", include("post.urls", namespace="post")),
    path("a/", include("files.admin_urls")),
    path("a/", include("trips.urls")),
    path("a/", include("plugins.urls")),
    path("a/wordpress/", include("wordpress.urls", namespace="wordpress")),
    path("a/", include("indieweb.urls", namespace="indieweb")),
    path("files/", include("files.urls")),
    path("", include("feeds.urls", namespace="feeds")),
    path("webmention/", include("webmention.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
]

# Include any plugin urls after core urls.
plugin_urls = [path("", include(plugin_urls)) for plugin_urls in plugin_pool.urls()]
urlpatterns.extend(plugin_urls)

# Public urls are last so "slug-like" urls in plugins are not matched to the stream-list view.
urlpatterns.append(
    path("", include("public.urls", namespace="public")),
)


handler404 = views.handle404

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
