import mf2py
import pytest
from django.contrib.gis.geos import Point
from model_bakery import baker

from core.constants import Visibility
from data.indieweb.constants import MPostKinds


@pytest.mark.django_db
@pytest.mark.freeze_time("2020-09-28 12:59:30")
class TestReplyRendering:
    @pytest.fixture
    def m_post_kind(self, m_post_kinds):
        return m_post_kinds.get(key=MPostKinds.reply)

    @pytest.fixture
    def t_entry(self, t_post, m_post_kind):
        return baker.make(
            "entry.TEntry",
            t_post=t_post,
            p_summary="Content here",
            e_content="<h1>Content here</h1>",
        )

    @pytest.fixture
    def t_reply(self, t_entry):
        return baker.make(
            "entry.TReply",
            t_entry=t_entry,
            u_in_reply_to="https://jamesvandyne.com/2021/03/02/2021-09.html",
            title="The Week #34",
            quote="I started working on replies in Tanzawa.",
            author="James",
            author_url="https://jamesvandyne.com/author/jamesvandyne",
            author_photo="",
        )

    def test_microformats_data(self, client, t_reply, t_entry, t_post):
        response = client.get(t_post.get_absolute_url())
        assert response.status_code == 200
        parsed = mf2py.parse(doc=response.content.decode("utf8"))
        reply = parsed["items"][0]
        assert reply == {
            "type": ["h-entry"],
            "properties": {
                "name": ["Response to The Week #34"],
                "in-reply-to": ["https://jamesvandyne.com/2021/03/02/2021-09.html"],
                "published": ["2020-09-28T12:59:30+00:00"],
                "author": [
                    {
                        "type": ["h-card"],
                        "properties": {
                            "photo": [
                                "https://www.gravatar.com/avatar/18780d317432b028f57e31756e34d181?d=mm&r=g&s=80 2x"
                            ],
                            "name": ["James"],
                            "url": ["http://testserver/author/jamesvandyne/"],
                            "uid": ["http://testserver/author/jamesvandyne/"],
                        },
                        "value": "James",
                    }
                ],
                "content": [
                    {
                        "html": "<blockquote>I started working on replies in Tanzawa.</blockquote>\n"
                        "        <h1>Content here</h1>",
                        "value": "I started working on replies in Tanzawa. Content here",
                    }
                ],
                "url": ["http://testserver/90a0027d-9c74-44e8-895c-6d5611f8eca5"],
            },
        }


@pytest.mark.django_db
@pytest.mark.freeze_time("2020-09-28 12:59:30")
class TestBookmarkRendering:
    @pytest.fixture
    def m_post_kind(self, m_post_kinds):
        return m_post_kinds.get(key=MPostKinds.bookmark)

    @pytest.fixture
    def t_entry(self, t_post, m_post_kind):
        return baker.make(
            "entry.TEntry",
            t_post=t_post,
            p_summary="Content here",
            e_content="<h1>Content here</h1>",
        )

    @pytest.fixture
    def t_bookmark(self, t_entry):
        return baker.make(
            "entry.TBookmark",
            t_entry=t_entry,
            u_bookmark_of="https://jamesvandyne.com/2021/03/02/2021-09.html",
            title="The Week #34",
            quote="I started working on replies in Tanzawa.",
            author="James",
            author_url="https://jamesvandyne.com/author/jamesvandyne",
            author_photo="",
        )

    def test_microformats_data(self, client, t_bookmark, t_entry, t_post):
        response = client.get(t_post.get_absolute_url())
        assert response.status_code == 200
        parsed = mf2py.parse(doc=response.content.decode("utf8"))
        bookmark = parsed["items"][0]
        assert bookmark == {
            "type": ["h-entry"],
            "properties": {
                "name": ["Bookmark of The Week #34"],
                "bookmark-of": [
                    {
                        "type": ["h-cite"],
                        "properties": {
                            "name": ["The Week #34"],
                            "url": ["https://jamesvandyne.com/2021/03/02/2021-09.html"],
                        },
                        "value": "https://jamesvandyne.com/2021/03/02/2021-09.html",
                    }
                ],
                "published": ["2020-09-28T12:59:30+00:00"],
                "author": [
                    {
                        "type": ["h-card"],
                        "properties": {
                            "photo": [
                                "https://www.gravatar.com/avatar/18780d317432b028f57e31756e34d181?d=mm&r=g&s=80 2x"
                            ],
                            "name": ["James"],
                            "uid": ["http://testserver/author/jamesvandyne/"],
                            "url": ["http://testserver/author/jamesvandyne/"],
                        },
                        "value": "James",
                    }
                ],
                "content": [
                    {
                        "html": "<blockquote>I started working on replies in Tanzawa.</blockquote>\n"
                        "        <h1>Content here</h1>",
                        "value": "I started working on replies in Tanzawa. Content here",
                    }
                ],
                "url": ["http://testserver/90a0027d-9c74-44e8-895c-6d5611f8eca5"],
            },
        }


@pytest.mark.django_db
@pytest.mark.freeze_time("2020-09-28 12:59:30")
class TestArticleRendering:
    @pytest.fixture
    def m_post_kind(self, m_post_kinds):
        return m_post_kinds.get(key=MPostKinds.article)

    @pytest.fixture
    def t_entry(self, t_post, m_post_kind):
        return baker.make(
            "entry.TEntry",
            t_post=t_post,
            p_name="My Awesome Post",
            p_summary="Content here",
            e_content="<h1>Content here</h1>",
        )

    @pytest.fixture
    def t_syndication(self, t_entry):
        return baker.make(
            "entry.TSyndication",
            t_entry=t_entry,
            url="https://twitter.com/jamesvandyne/status/1372676240998428673",
        )

    @pytest.fixture
    def t_location(self, t_entry):
        return baker.make(
            "entry.TLocation",
            t_entry=t_entry,
            locality="Fujisawa",
            region="Kanagawa",
            country_name="Japan",
            point=Point(
                y=35.31593281000502,
                x=139.4700015160363,
            ),
        )

    def test_microformats_data(self, client, t_entry, t_post, t_syndication, t_location):
        response = client.get(t_post.get_absolute_url())
        assert response.status_code == 200
        parsed = mf2py.parse(doc=response.content.decode("utf8"))
        article = parsed["items"][0]

        assert article == {
            "type": ["h-entry"],
            "properties": {
                "name": ["My Awesome Post"],
                "published": ["2020-09-28T12:59:30+00:00"],
                "syndication": ["https://twitter.com/jamesvandyne/status/1372676240998428673"],
                "location": [
                    {
                        "type": ["h-adr"],
                        "properties": {
                            "latitude": ["35.31593281000502"],
                            "longitude": ["139.4700015160363"],
                            "label": ["Fujisawa, Kanagawa, Japan"],
                        },
                        "value": "35.31593281000502 139.4700015160363 Fujisawa, Kanagawa, Japan",
                    }
                ],
                "author": [
                    {
                        "type": ["h-card"],
                        "properties": {
                            "photo": [
                                "https://www.gravatar.com/avatar/18780d317432b028f57e31756e34d181?d=mm&r=g&s=80 2x"
                            ],
                            "name": ["James"],
                            "url": ["http://testserver/author/jamesvandyne/"],
                            "uid": ["http://testserver/author/jamesvandyne/"],
                        },
                        "value": "James",
                    }
                ],
                "content": [{"html": "<h1>Content here</h1>", "value": "Content here"}],
                "url": ["http://testserver/90a0027d-9c74-44e8-895c-6d5611f8eca5"],
            },
        }


@pytest.mark.django_db
@pytest.mark.freeze_time("2020-09-28 12:59:30")
class TestNoteRendering:
    @pytest.fixture
    def m_post_kind(self, m_post_kinds):
        return m_post_kinds.get(key=MPostKinds.note)

    @pytest.fixture
    def t_entry(self, t_post, m_post_kind):
        return baker.make(
            "entry.TEntry",
            t_post=t_post,
            p_name="",
            p_summary="Content here",
            e_content="<h1>Content here</h1>",
        )

    def test_microformats_data(self, client, t_entry, t_post):
        response = client.get(t_post.get_absolute_url())
        assert response.status_code == 200
        parsed = mf2py.parse(doc=response.content.decode("utf8"))
        note = parsed["items"][0]
        assert note == {
            "type": ["h-entry"],
            "properties": {
                "published": ["2020-09-28T12:59:30+00:00"],
                "author": [
                    {
                        "type": ["h-card"],
                        "properties": {
                            "photo": [
                                "https://www.gravatar.com/avatar/18780d317432b028f57e31756e34d181?d=mm&r=g&s=80 2x"
                            ],
                            "name": ["James"],
                            "url": ["http://testserver/author/jamesvandyne/"],
                            "uid": ["http://testserver/author/jamesvandyne/"],
                        },
                        "value": "James",
                    }
                ],
                "content": [{"html": "<h1>Content here</h1>", "value": "Content here"}],
                "url": ["http://testserver/90a0027d-9c74-44e8-895c-6d5611f8eca5"],
            },
        }


@pytest.mark.django_db
@pytest.mark.freeze_time("2020-09-28 12:59:30")
class TestPermalinkView:
    @pytest.fixture
    def m_post_kind(self, m_post_kinds):
        return m_post_kinds.get(key=MPostKinds.note)

    @pytest.fixture
    def t_post(self, t_post, author, visibility):
        t_post.p_author = author
        t_post.visibility = visibility
        t_post.save()
        return t_post

    @pytest.fixture
    def t_entry(self, t_post, m_post_kind, author):
        return baker.make(
            "entry.TEntry",
            t_post=t_post,
            p_name="",
            p_summary="Content here",
            e_content="<h1>Content here</h1>",
        )

    @pytest.fixture
    def author(self):
        return baker.make("auth.User", username="Author")

    @pytest.fixture
    def another_user(self):
        return baker.make("auth.User", username="Another")

    @pytest.mark.parametrize(
        "visibility,status_code,login_user",
        [
            (Visibility.PUBLIC, 200, None),
            (Visibility.PRIVATE, 404, None),
            (Visibility.UNLISTED, 200, None),
            (Visibility.PUBLIC, 200, pytest.lazy_fixture("author")),
            (Visibility.PRIVATE, 200, pytest.lazy_fixture("author")),
            (Visibility.UNLISTED, 200, pytest.lazy_fixture("author")),
            (Visibility.PUBLIC, 200, pytest.lazy_fixture("another_user")),
            (Visibility.PRIVATE, 404, pytest.lazy_fixture("another_user")),
            (Visibility.UNLISTED, 200, pytest.lazy_fixture("another_user")),
        ],
    )
    def test_respects_visibility(
        self, client, t_entry, t_post, author, another_user, visibility, status_code, login_user
    ):
        if login_user:
            client.force_login(login_user)
        response = client.get(t_post.get_absolute_url())
        assert response.status_code == status_code
