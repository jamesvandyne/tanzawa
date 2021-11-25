from django.contrib import messages
from django.shortcuts import redirect, render
from plugins.core import plugin_pool
from django.contrib.auth import decorators as auth_decorators


@auth_decorators.login_required
def plugin_list(request):

    return render(
        request,
        "plugins/plugin_list.html",
        {
            "available_plugins": plugin_pool.get_all_plugins(),
            "nav": "plugins",
            "page_title": "Plugins"
        },
    )


@auth_decorators.login_required
def enable_plugin(request, identifier: str):
    plugin = plugin_pool.get_plugin(identifier)
    if not plugin:
        messages.error(request, "Plugin not found.")
        return redirect("plugins:plugin_list")
    plugin_pool.enable(plugin)
    messages.success(request, f"{plugin.name} enabled.")
    return redirect("plugins:plugin_list")


@auth_decorators.login_required
def disable_plugin(request, identifier: str):
    plugin = plugin_pool.get_plugin(identifier)
    if not plugin:
        messages.error(request, "Plugin not found.")
        return redirect("plugins:plugin_list")
    plugin_pool.disable(plugin)
    messages.success(request, f"{plugin.name} disabled.")
    return redirect("plugins:plugin_list")
