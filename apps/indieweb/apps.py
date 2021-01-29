from django.apps import AppConfig


class IndiewebConfig(AppConfig):
    name = "indieweb"

    def ready(self):
        import indieweb.handlers  # noqa: F401
