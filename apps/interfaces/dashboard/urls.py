from django.urls import include, path
from django.utils import text
from plugins import pool

urlpatterns = [
    path("", include("interfaces.dashboard.entry.urls")),
]

# Include any plugin urls after core urls.
plugin_urls = [path("", include(plugin_urls)) for plugin_urls in pool.plugin_pool.urls()]
urlpatterns.extend(plugin_urls)

plugin_admin_urls = [
    path(f"a/plugins/{text.slugify(plugin.name)}/", include(plugin.admin_urls))
    for plugin in pool.plugin_pool.enabled_plugins()
    if plugin.admin_urls
]
urlpatterns.extend(plugin_admin_urls)
