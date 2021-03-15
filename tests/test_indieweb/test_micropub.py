from typing import Dict, Any
from unittest.mock import Mock

import pytest
from entry.models import TEntry, TReply, TBookmark, TLocation, TCheckin
from unittest.mock import Mock
from post.models import TPost


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

    @pytest.mark.freeze_time("2021-02-13 12:30:59")
    def test_handles_embeded_base64_images(
        self,
        target,
        client,
        t_token_access,
        auth_token,
        client_id,
        mock_send_webmention,
    ):
        """A post made from the article poster on Quill"""
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")

        data = {
            "type": ["h-entry"],
            "properties": {
                "name": ["A neat title"],
                "content": [
                    {
                        "html": '<p>This is a neat title</p>\n<h2>\n  Subtitle\n  <br />\n</h2>\n<p><b>Hello</b></p>\n<figure>\n  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAFBlWElmTU0AKgAAAAgAAgESAAMAAAABAAEAAIdpAAQAAAABAAAAJgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAAaADAAQAAAABAAAAAQAAAADr/7PgAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAAADUlEQVQIHWP4/f39fwAJswPh+tQCZAAAAABJRU5ErkJggg==" alt="" />\n</figure>'
                    }
                ],
                "category": ["photos", "checkins", "fake"],
            },
        }
        response = client.post(target, data=data, format="json")

        assert response.status_code == 201

        t_entry = TEntry.objects.last()
        t_post: TPost = t_entry.t_post
        assert t_post.m_post_kind.key == "article"
        assert t_post.m_post_status.key == "published"

        assert t_post.files.count() == 1

        assert t_post.streams.count() == 2
        assert t_post.streams.filter(slug="photos").exists()
        assert t_post.streams.filter(slug="checkins").exists()

        t_file = t_post.files.first()

        assert t_file.mime_type == "image/png"
        assert t_file.filename == "2021-02-13T12:30:59.png"

        assert str(t_file.uuid) in t_entry.e_content
        assert t_entry.p_summary.startswith("This is a neat title")
        assert t_entry.p_name == "A neat title"

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
        t_post: TPost = t_entry.t_post

        assert t_post.m_post_kind.key == "note"
        assert t_post.m_post_status.key == "published"

        assert t_post.files.count() == 1

        t_file = t_post.files.first()

        assert t_file.mime_type == "image/png"
        assert t_file.filename == "1px.png"

        assert str(t_file.uuid) in t_entry.e_content
        assert t_entry.p_summary == "Test with a photo"

    @pytest.fixture
    def parsed_linked_page(self):
        from indieweb.extract import LinkedPage, LinkedPageAuthor

        return LinkedPage(
            url="https://jamesvandyne.com/2021/03/02/2021-09.html",
            title="The Week #34",
            description="I forget what I was searching for but I found this fantastic blog",
            author=LinkedPageAuthor(
                name="James",
                url="https://jamesvandyne.com/author/jamesvandyne",
                photo=None,
            ),
        )

    @pytest.fixture
    def mock_extract_reply(self, monkeypatch, parsed_linked_page):
        from indieweb.extract import extract_reply_details_from_url

        m = Mock(extract_reply_details_from_url, autospec=True)
        m.return_value = parsed_linked_page
        monkeypatch.setattr("indieweb.serializers.extract_reply_details_from_url", m)
        return m

    def test_post_replies_mf2(
        self,
        target,
        client,
        t_token_access,
        auth_token,
        client_id,
        mock_send_webmention,
        mock_extract_reply,
    ):
        data = {
            "type": ["h-entry"],
            "properties": {
                "h": ["entry"],
                "content": [
                    "This is a test reply from quill so I can add replies to micropub!"
                ],
                "in-reply-to": ["https://jamesvandyne.com/2021/03/02/2021-09.html"],
                "category": ["replies"],
            },
        }
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
        response = client.post(target, data=data, format="json")
        assert response.status_code == 201

        t_entry = TEntry.objects.last()
        t_post: TPost = t_entry.t_post

        assert t_post.m_post_kind.key == "reply"
        assert t_post.m_post_status.key == "published"

        assert t_entry.p_summary.startswith(data["properties"]["content"][0])

        t_reply: TReply = t_entry.t_reply

        assert t_reply.u_in_reply_to == data["properties"]["in-reply-to"][0]
        assert t_reply.author == "James"
        assert t_reply.title == "The Week #34"
        assert (
            t_reply.quote
            == "I forget what I was searching for but I found this fantastic blog"
        )

        mock_extract_reply.assert_called_once()

    def test_post_replies_form(
        self,
        target,
        client,
        t_token_access,
        auth_token,
        client_id,
        mock_send_webmention,
        mock_extract_reply,
    ):
        data = {
            "h": ["entry"],
            "access_token": [auth_token],
            "content": [
                "This is a test reply from quill so I can add replies to micropub!"
            ],
            "in-reply-to": ["https://jamesvandyne.com/2021/03/02/2021-09.html"],
            "category": ["replies"],
        }

        response = client.post(target, data=data)
        assert response.status_code == 201

        t_entry = TEntry.objects.last()
        t_post: TPost = t_entry.t_post

        assert t_post.m_post_kind.key == "reply"
        assert t_post.m_post_status.key == "published"

        assert t_entry.p_summary.startswith(data["content"][0])

        t_reply: TReply = t_entry.t_reply

        assert t_reply.u_in_reply_to == data["in-reply-to"][0]
        assert t_reply.author == "James"
        assert t_reply.title == "The Week #34"
        assert (
            t_reply.quote
            == "I forget what I was searching for but I found this fantastic blog"
        )

        mock_extract_reply.assert_called_once()

    def test_post_bookmark_form(
        self,
        target,
        client,
        t_token_access,
        auth_token,
        client_id,
        mock_send_webmention,
        mock_extract_reply,
    ):
        data = {
            "h": ["entry"],
            "access_token": [auth_token],
            "content": [
                "This is a test a book from quill so I can add replies to micropub!"
            ],
            "bookmark-of": ["https://jamesvandyne.com/2021/03/02/2021-09.html"],
            "category": ["bookmarks"],
        }

        response = client.post(target, data=data)
        assert response.status_code == 201

        t_entry = TEntry.objects.last()
        t_post: TPost = t_entry.t_post

        assert t_post.m_post_kind.key == "bookmark"
        assert t_post.m_post_status.key == "published"

        assert t_entry.p_summary.startswith(data["content"][0])

        t_bookmark: TBookmark = t_entry.t_bookmark

        assert t_bookmark.u_bookmark_of == data["bookmark-of"][0]
        assert t_bookmark.author == "James"
        assert t_bookmark.title == "The Week #34"
        assert (
            t_bookmark.quote
            == "I forget what I was searching for but I found this fantastic blog"
        )

        mock_extract_reply.assert_called_once()

    @pytest.fixture
    def entry_with_location(self) -> Dict[str, Any]:
        return {
            "type": ["h-entry"],
            "properties": {
                "published": ["2021-01-02T13:57:54+09:00"],
                "syndication": [
                    "https://www.swarmapp.com/user/89277993/checkin/5feffd52060f7b279432fca3"
                ],
                "content": ["\u98fd\u304d\u306a\u3044\u306a\u3041\u30fc"],
                "photo": [
                    "https://fastly.4sqi.net/img/general/original/89277993_vrz-_zxqAWoYCNJFnaaDWHpyAD7cJUPojCwRzTDJewE.jpg"
                ],
                "category": ["check-in"],
                "location": [
                    {
                        "type": ["h-adr"],
                        "properties": {
                            "latitude": [35.31593281000502],
                            "longitude": [139.4700015160363],
                            "street-address": ["\u9d60\u6cbc\u6d77\u5cb8"],
                            "locality": ["Fujisawa"],
                            "region": ["Kanagawa"],
                            "country-name": ["Japan"],
                            "postal-code": ["251-0037"],
                        },
                    }
                ],
            },
        }

    @pytest.fixture
    def checkin_entry(self, entry_with_location):
        entry_with_location["properties"].update(
            {
                "checkin": [
                    {
                        "type": ["h-card"],
                        "properties": {
                            "name": ["Kugenuma Beach (\u9d60\u6cbc\u6d77\u5cb8)"],
                            "url": [
                                "https://foursquare.com/v/4bf726e25ec320a1e18a86d3"
                            ],
                            "latitude": [35.31593281000502],
                            "longitude": [139.4700015160363],
                            "street-address": ["\u9d60\u6cbc\u6d77\u5cb8"],
                            "locality": ["Fujisawa"],
                            "region": ["Kanagawa"],
                            "country-name": ["Japan"],
                            "postal-code": ["251-0037"],
                        },
                        "value": "https://foursquare.com/v/4bf726e25ec320a1e18a86d3",
                    }
                ]
            }
        )
        return entry_with_location

    def test_post_with_location(
        self,
        target,
        client,
        t_token_access,
        auth_token,
        client_id,
        mock_send_webmention,
        entry_with_location,
        download_image_mock,
    ):
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
        response = client.post(target, data=entry_with_location, format="json")
        assert response.status_code == 201

        t_entry = TEntry.objects.last()
        t_post: TPost = t_entry.t_post

        assert t_post.m_post_kind.key == "note"
        assert t_post.m_post_status.key == "published"
        assert t_post.dt_published.isoformat() == "2021-01-02T04:57:54+00:00"

        assert t_entry.p_summary == "飽きないなぁー"
        assert "飽きないなぁー" in t_entry.e_content
        assert "<figure" in t_entry.e_content

        t_location: TLocation = t_entry.t_location
        assert t_location.street_address == "鵠沼海岸"
        assert t_location.country_name == "Japan"
        assert t_location.postal_code == "251-0037"
        assert t_location.locality == "Fujisawa"
        assert t_location.point.x == 35.31593281000502
        assert t_location.point.y == 139.4700015160363

        download_image_mock.assert_called_with(
            entry_with_location["properties"]["photo"][0]
        )

    @pytest.fixture
    def download_image_mock(self, monkeypatch):
        from indieweb.utils import download_image, DataImage

        m = Mock(download_image, autospec=True)
        with open("tests/fixtures/1px.png", "rb") as photo:
            m.return_value = DataImage(
                image_data=photo.read(),
                mime_type="image/png",
                encoding="none",
                tag=None,
            )
        monkeypatch.setattr("indieweb.serializers.download_image", m)
        return m

    def test_post_with_checkin(
        self,
        target,
        client,
        t_token_access,
        auth_token,
        client_id,
        mock_send_webmention,
        checkin_entry,
        download_image_mock,
    ):
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
        response = client.post(target, data=checkin_entry, format="json")
        assert response.status_code == 201

        t_entry = TEntry.objects.last()
        t_post: TPost = t_entry.t_post

        assert t_post.m_post_kind.key == "checkin"
        assert t_post.m_post_status.key == "published"
        assert t_post.dt_published.isoformat() == "2021-01-02T04:57:54+00:00"

        assert t_entry.p_summary == "飽きないなぁー"
        assert "飽きないなぁー" in t_entry.e_content
        assert "<figure" in t_entry.e_content

        t_location: TLocation = t_entry.t_location
        assert t_location.street_address == "鵠沼海岸"
        assert t_location.country_name == "Japan"
        assert t_location.postal_code == "251-0037"
        assert t_location.locality == "Fujisawa"
        assert t_location.point.x == 35.31593281000502
        assert t_location.point.y == 139.4700015160363

        t_checkin: TCheckin = t_entry.t_checkin

        assert t_checkin.t_location == t_location
        assert t_checkin.url == "https://foursquare.com/v/4bf726e25ec320a1e18a86d3"
        assert t_checkin.name == "Kugenuma Beach (鵠沼海岸)"

        assert t_post.files.count() == 1

        download_image_mock.assert_called_with(checkin_entry["properties"]["photo"][0])
