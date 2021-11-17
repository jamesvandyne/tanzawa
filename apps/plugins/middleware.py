from .core import plugin_pool


class PluginMiddleware:
    """
    Makes the plugin pool available on the request.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.plugins = plugin_pool.get_all_plugins()

    def __call__(self, request):
        # Store the plugins on the request object so we can access them when rendering.
        request.plugin_pool = plugin_pool
        response = self.get_response(request)

        # TODO: Add post response hooks to plugin

        return response
