from django import apps


class IndiewebConfig(apps.AppConfig):
    name = "data.indieweb"

    def ready(self):
        from . import handlers  # noqa: F401
