import pytest
from model_bakery import baker
from indieweb.constants import MPostKinds, MPostStatuses
import mf2py
from django.contrib.gis.geos import Point


@pytest.fixture
def m_post_kinds():
    from post.models import MPostKind

    return MPostKind.objects.all()


@pytest.fixture
def m_post_kind(m_post_kinds):
    return m_post_kinds[0]  # note


@pytest.fixture
def published_status():
    from post.models import MPostStatus

    return MPostStatus.objects.get(key=MPostStatuses.published)


@pytest.fixture
def user():
    return baker.make(
        "User",
        username="jamesvandyne",
        first_name="James",
        last_name="Van Dyne",
        email="james@example.test",
    )


@pytest.fixture
def t_post(m_post_kind, published_status, user):
    from datetime import datetime

    return baker.make(
        "post.TPost",
        m_post_status=published_status,
        m_post_kind=m_post_kind,
        p_author=user,
        dt_published=datetime.now(),
        uuid="90a0027d-9c74-44e8-895c-6d5611f8eca5",
    )


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
                "content": [{"html": "<h1>Content here</h1>", "value": "Content here"}],
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
                "content": [{"html": "<h1>Content here</h1>", "value": "Content here"}],
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
                35.31593281000502,
                139.4700015160363,
            ),
        )

    def test_microformats_data(
        self, client, t_entry, t_post, t_syndication, t_location
    ):
        response = client.get(t_post.get_absolute_url())
        assert response.status_code == 200
        parsed = mf2py.parse(doc=response.content.decode("utf8"))
        article = parsed["items"][0]

        assert article == {
            "type": ["h-entry"],
            "properties": {
                "name": ["My Awesome Post"],
                "published": ["2020-09-28T12:59:30+00:00"],
                "syndication": [
                    "https://twitter.com/jamesvandyne/status/1372676240998428673"
                ],
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
