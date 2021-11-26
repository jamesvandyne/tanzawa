from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
from django.shortcuts import redirect, render
from plugins import pool


@auth_decorators.login_required
def plugin_list(request):

    return render(
        request,
        "plugins/plugin_list.html",
        {"available_plugins": pool.plugin_pool.get_all_plugins(), "nav": "plugins", "page_title": "Plugins"},
    )


@auth_decorators.login_required
def enable_plugin(request, identifier: str):
    plugin = pool.plugin_pool.get_plugin(identifier)
    if not plugin:
        messages.error(request, "Plugin not found.")
        return redirect("plugins:plugin_list")
    pool.plugin_pool.enable(plugin)
    messages.success(request, f"{plugin.name} enabled.")
    return redirect("plugins:plugin_list")


@auth_decorators.login_required
def disable_plugin(request, identifier: str):
    plugin = pool.plugin_pool.get_plugin(identifier)
    if not plugin:
        messages.error(request, "Plugin not found.")
        return redirect("plugins:plugin_list")
    pool.plugin_pool.disable(plugin)
    messages.success(request, f"{plugin.name} disabled.")
    return redirect("plugins:plugin_list")
