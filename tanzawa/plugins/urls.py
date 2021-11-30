from django.urls import path, re_path

from . import views

app_name = "plugins"

urlpatterns = [
    path("plugins/", views.plugin_list, name="plugin_list"),
    re_path(r"^plugins/(?P<identifier>[a-z.]+)/enable/$", views.enable_plugin, name="plugin_enable"),
    re_path(r"^plugins/(?P<identifier>[a-z.]+)/disable/$", views.disable_plugin, name="plugin_disable"),
]
