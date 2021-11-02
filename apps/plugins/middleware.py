from django.conf import settings
from django.utils import module_loading


class PluginMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.plugins = []
        # init each plugin
        for plugin_path in settings.PLUGINS:
            plugin = module_loading.import_string(plugin_path)
            self.plugins.append(plugin.get_plugin())

    def __call__(self, request):
        # Store the plugins on the request object so we can access them when rendering.
        request.plugins = self.plugins
        response = self.get_response(request)

        # TODO: Add post response hooks to plugin

        return response