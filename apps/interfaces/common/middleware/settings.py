from data.settings.models import MSiteSettings


class SettingsMiddleware:
    """Set our settings object on the request"""

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request.settings = MSiteSettings.objects.first() or MSiteSettings()
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
