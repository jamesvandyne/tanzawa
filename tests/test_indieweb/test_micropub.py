import pytest
from entry.models import TEntry
from unittest.mock import Mock


@pytest.mark.django_db
class TestMicropub:
    @pytest.fixture
    def target(self):
        return "/a/micropub/"

    @pytest.fixture
    def entry_data(self):
        return {
            "h": "entry",
            "content": "hello world",
            "action": "create",
        }

    @pytest.fixture
    def quill_note(self, auth_token):
        return {
            "h": ["entry"],
            "access_token": [auth_token],
            "content": ["This is some test content"],
            "location": ["geo:35.5173,139.61426;u=65"],
            "category[]": ["japan", "tech", "tanzawa"],
        }

    @pytest.fixture
    def mock_send_webmention(self, monkeypatch):
        from indieweb.webmentions import send_webmention

        m = Mock(autospec=send_webmention)
        monkeypatch.setattr("indieweb.views.send_webmention", m)
        return m

    def test_token_create(
        self,
        target,
        client,
        t_token_access,
        auth_token,
        client_id,
        quill_note,
        mock_send_webmention,
    ):
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
        response = client.post(target, data=quill_note)
        assert response.status_code == 201
        assert TEntry.objects.count() == 1
        assert mock_send_webmention.called

    def test_form_data_create(
        self,
        target,
        client,
        t_token_access,
        auth_token,
        client_id,
        quill_note,
        mock_send_webmention,
    ):
        quill_note.update({"access_token": auth_token})
        response = client.post(target, data=quill_note)

        assert response.status_code == 201

    def test_validates_scope(
        self,
        target,
        client,
        t_token_access,
        auth_token,
        client_id,
        quill_note,
        mock_send_webmention,
    ):
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
        quill_note["action"] = "delete"
        response = client.post(target, data=quill_note)
        assert response.status_code == 400
        assert response.json() == {
            "non_field_errors": ["Token does not have delete permissions"]
        }
