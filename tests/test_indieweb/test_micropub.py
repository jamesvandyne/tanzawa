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

    def test_handles_embeded_base64_images(self):
        """A post made from the article poster on Quill"""
        data = {
            "type": ["h-entry"],
            "properties": {
                "name": ["A neat title"],
                "content": [
                    {
                        "html": '<p>This is a neat title</p>\n<h2>\n  Subtitle\n  <br />\n</h2>\n<p><b>Hello</b></p>\n<figure>\n  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAFBlWElmTU0AKgAAAAgAAgESAAMAAAABAAEAAIdpAAQAAAABAAAAJgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAAaADAAQAAAABAAAAAQAAAADr/7PgAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAAADUlEQVQIHWP4/f39fwAJswPh+tQCZAAAAABJRU5ErkJggg==" alt="" />\n</figure>'
                    }
                ],
            },
        }
        assert data

    def test_handles_photo_attachments(
        self,
        target,
        client,
        t_token_access,
        auth_token,
        client_id,
        mock_send_webmention,
    ):
        with open("tests/fixtures/1px.png", "rb") as photo:
            data = {
                "h": "entry",
                "access_token": auth_token,
                "content": "Test with a photo",
                "photo": [photo],
            }
            response = client.post(target, data=data)
            assert response.status_code == 201

        t_entry = TEntry.objects.last()
        t_post = t_entry.t_post

        assert t_post.files.count() == 1

        t_file = t_post.files.first()

        assert t_file.mime_type == "image/png"
        assert t_file.filename == "1px.png"

        assert str(t_file.uuid) in t_entry.e_content
        assert t_entry.p_summary == "Test with a photo"
