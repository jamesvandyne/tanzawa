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
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from . import views


urlpatterns = [
    path("a/", include("entry.urls")),
    path("a/", include("post.urls", namespace="post")),
    path("a/wordpress/", include("wordpress.urls", namespace="wordpress")),
    path("a/", include("indieweb.urls", namespace="indieweb")),
    path("files/", include("files.urls")),
    path("", include("feeds.urls", namespace="feeds")),
    path("webmention/", include("webmention.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("", include("public.urls", namespace="public")),
]

handler404 = views.handle404

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
