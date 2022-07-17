from django import apps


class HealthConfig(apps.AppConfig):
    name = "tanzawa_plugin.health"


default_app_config = "tanzawa_plugin.health.apps.HealthConfig"
