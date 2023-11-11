from django.conf import settings
from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import redirect, render
from django.views.decorators import http

from data.plugins import pool


@auth_decorators.login_required
def plugin_list(request):
    return render(
        request,
        "plugins/plugin_list.html",
        {"available_plugins": pool.plugin_pool.get_all_plugins(), "nav": "plugins", "page_title": "Plugins"},
    )


@auth_decorators.login_required
@http.require_POST
def enable_plugin(request, identifier: str):
    plugin = pool.plugin_pool.get_plugin(identifier)
    if not plugin:
        messages.error(request, "Plugin not found.")
        return redirect("plugin_list")
    pool.plugin_pool.enable(plugin)
    fly_app_message = (
        f"Run flyctl app restart {settings.FLY_APP_NAME} for changes to take effect." if settings.FLY_APP_NAME else ""
    )
    messages.success(request, f"{plugin.name} enabled. {fly_app_message}")
    return redirect("plugin_list")


@auth_decorators.login_required
@http.require_POST
def disable_plugin(request, identifier: str):
    plugin = pool.plugin_pool.get_plugin(identifier)
    if not plugin:
        messages.error(request, "Plugin not found.")
        return redirect("plugin_list")
    pool.plugin_pool.disable(plugin)
    fly_app_message = (
        f"Run flyctl app restart {settings.FLY_APP_NAME} for changes to take effect." if settings.FLY_APP_NAME else ""
    )
    messages.success(request, f"{plugin.name} disabled. {fly_app_message}")
    return redirect("plugin_list")
