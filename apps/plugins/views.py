from plugins.core import plugin_pool

from django.shortcuts import render, redirect
from django.contrib import messages


def plugin_list(request):

    return render(
        request,
        "plugins/plugin_list.html",
        {
            "available_plugins": plugin_pool.get_all_plugins(),
        },
    )


def enable_plugin(request, identifier: str):
    plugin = plugin_pool.get_plugin(identifier)
    if not plugin:
        messages.error(request, "Plugin not found.")
        return redirect("plugins:plugin_list")
    plugin_pool.enable(plugin)
    messages.success(request, f"{plugin.name} enabled.")
    return redirect("plugins:plugin_list")


def disable_plugin(request, identifier: str):
    plugin = plugin_pool.get_plugin(identifier)
    if not plugin:
        messages.error(request, "Plugin not found.")
        return redirect("plugins:plugin_list")
    plugin_pool.disable(plugin)
    messages.success(request, f"{plugin.name} disabled.")
    return redirect("plugins:plugin_list")
