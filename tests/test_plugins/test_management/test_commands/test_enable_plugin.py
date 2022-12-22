from unittest import mock

import pytest
from django.core import management

from data.plugins import models as plugin_models


@pytest.mark.django_db
class TestEnablePlugin:
    @mock.patch("data.plugins.activation.management")
    def test_can_enable_plugin(self, management_mock):
        identifier = "blog.tanzawa.plugins.nowpage"
        management.call_command("enable_plugin", identifier)

        # Plugin is enabled
        m_plugin = plugin_models.MPlugin.objects.get(identifier=identifier)
        assert m_plugin.enabled is True

        management_mock.call_command.assert_called_with("migrate", "now", interactive=False)

    @mock.patch("data.plugins.activation.management")
    def test_errs_if_not_found(self, management_mock):
        identifier = "com.example.hoge"

        with pytest.raises(management.CommandError):
            management.call_command("enable_plugin", identifier)

        # Plugin is enabled
        assert plugin_models.MPlugin.objects.filter(identifier=identifier).exists() is False
        management_mock.call_command.assert_not_called()
