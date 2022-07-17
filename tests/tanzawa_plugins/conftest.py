import pytest


@pytest.fixture(autouse=True)
def enable_health(factory):
    from tanzawa_plugin.health import plugin

    factory.MPlugin(identifier=plugin.__identifier__, enabled=True)
