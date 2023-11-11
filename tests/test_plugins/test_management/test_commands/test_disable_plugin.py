import pytest
from django.core import management
from model_bakery import baker


@pytest.mark.django_db
class TestDisablePlugin:
    def test_can_disable_plugin(
        self,
    ):
        identifier = "blog.tanzawa.plugins.nowpage"
        m_plugin = baker.make("plugins.MPlugin", identifier=identifier, enabled=True)

        management.call_command("disable_plugin", identifier)

        # Plugin is disabled
        m_plugin.refresh_from_db()
        assert m_plugin.enabled is False

    def test_errs_if_not_found(self):
        identifier = "com.example.hoge"

        with pytest.raises(management.CommandError):
            management.call_command("disable_plugin", identifier)
