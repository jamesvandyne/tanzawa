import pytest
from django.core import management

from data.plugins import models as plugin_models


@pytest.mark.django_db
class TestEnablePlugin:
    def test_can_enable_plugin(self):
        identifier = "blog.tanzawa.plugins.nowpage"
        management.call_command("enable_plugin", identifier)

        # Plugin is enabled
        m_plugin = plugin_models.MPlugin.objects.get(identifier=identifier)
        assert m_plugin.enabled is True

    def test_errs_if_not_found(
        self,
    ):
        identifier = "com.example.hoge"

        with pytest.raises(management.CommandError):
            management.call_command("enable_plugin", identifier)

        # Plugin is enabled
        assert plugin_models.MPlugin.objects.filter(identifier=identifier).exists() is False
