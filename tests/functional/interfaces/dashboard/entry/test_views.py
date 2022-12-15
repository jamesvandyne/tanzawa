from decimal import Decimal
from unittest import mock

import pytest
from core.constants import Visibility
from data.entry import models as entry_models
from django.contrib.gis import geos
from django.urls import reverse


@pytest.mark.django_db
class TestCreateStatusView:
    @mock.patch("application.indieweb.webmentions.ronkyuu")
    def test_create_status_entry_view(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: A post to create a new status entry
        Expect: A new status to be created
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)
        #
        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
            "e_content": "<div>Hello</div>",
            "streams": str(stream.pk),
            # ... with a location in Japan
            "location-street_address": "+",
            "location-locality": "Kawauchi",
            "location-region": "Fukushima+Prefecture",
            "location-country_name": "Japan",
            "location-postal_code": "",
            "location-point": '{"type":"Point","coordinates":[140.80078125000003,37.31425771585506]}',
            # ... and has been syndicated...
            "syndication-TOTAL_FORMS": "1",
            "syndication-INITIAL_FORMS": "0",
            "syndication-MIN_NUM_FORMS": "0",
            "syndication-MAX_NUM_FORMS": "1000",
            "syndication-0-url": "https://hoge.com",
            "syndication-0-id": "",
            "syndication-0-t_entry": "",
            "syndication-__prefix__-url": "",
            "syndication-__prefix__-id": "",
            "syndication-__prefix__-t_entry": "",
            # ... and is published
            "m_post_status": ["published", "published"],
            # ... for everyone to see
            "visibility": "1",
            "t_trip": "",
        }

        # Submit and...
        response = client.post(reverse("status_create"), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry = entry_models.TEntry.objects.last()
        assert entry
        assert entry.e_content == "<div>Hello</div>"
        assert entry.p_summary == "Hello"

        # ... with a post
        t_post = entry.t_post
        assert t_post
        # ... that is visible and published
        assert t_post.m_post_status.key == "published"
        assert t_post.m_post_kind.key == "note"
        assert t_post.visibility == Visibility.PUBLIC

        # ... and it is in the specified stream
        assert list(entry.t_post.streams.all()) == [stream]

        # The post has also been syndicated...
        assert entry.t_syndication.count() == 1
        syndication = entry.t_syndication.first()

        assert syndication.url == "https://hoge.com"

        # ... and a location
        location = entry.t_location

        assert location.street_address == "+"
        assert location.locality == "Kawauchi"
        assert location.region == "Fukushima+Prefecture"
        assert location.country_name == "Japan"
        assert location.postal_code == ""

        point = geos.Point((Decimal("140.80078125000003"), Decimal("37.31425771585506")))
        assert location.point.x == point.x
        assert location.point.y == point.y

    @mock.patch("application.indieweb.webmentions.ronkyuu")
    def test_create_status_without_location(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: A post to create a new status entry
        Expect: A new status to be created
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)
        #
        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
            "e_content": "<div>Hello</div>",
            "streams": str(stream.pk),
            # ... with a location in Japan
            "location-street_address": "",
            "location-locality": "",
            "location-region": "",
            "location-country_name": "",
            "location-postal_code": "",
            "location-point": "",
            # ... and has been syndicated...
            "syndication-TOTAL_FORMS": "1",
            "syndication-INITIAL_FORMS": "0",
            "syndication-MIN_NUM_FORMS": "0",
            "syndication-MAX_NUM_FORMS": "1000",
            "syndication-0-url": "https://hoge.com",
            "syndication-0-id": "",
            "syndication-0-t_entry": "",
            "syndication-__prefix__-url": "",
            "syndication-__prefix__-id": "",
            "syndication-__prefix__-t_entry": "",
            # ... and is published
            "m_post_status": ["published", "published"],
            # ... for everyone to see
            "visibility": "1",
            "t_trip": "",
        }

        # Submit and...
        response = client.post(reverse("status_create"), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry = entry_models.TEntry.objects.last()
        assert entry
        assert entry.e_content == "<div>Hello</div>"
        assert entry.p_summary == "Hello"

        # ... with a post
        t_post = entry.t_post
        assert t_post
        # ... that is visible and published
        assert t_post.m_post_status.key == "published"
        assert t_post.m_post_kind.key == "note"
        assert t_post.visibility == Visibility.PUBLIC

        # ... and it is in the specified stream
        assert list(entry.t_post.streams.all()) == [stream]

        # The post has also been syndicated...
        assert entry.t_syndication.count() == 1
        syndication = entry.t_syndication.first()

        assert syndication.url == "https://hoge.com"

        # ... and no location
        with pytest.raises(entry_models.TLocation.DoesNotExist):
            entry.t_location


@pytest.mark.django_db
class TestCreateArticleView:
    @mock.patch("application.indieweb.webmentions.ronkyuu")
    def test_create_article_entry_view(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: A post to create a new article entry
        Expect: A new article to be created
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)
        #
        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
            "m_post_kind": "article",
            "p_name": "The Week",
            "e_content": "<div>Hello</div>",
            "streams": str(stream.pk),
            # ... with a location in Japan
            "location-street_address": "+",
            "location-locality": "Kawauchi",
            "location-region": "Fukushima+Prefecture",
            "location-country_name": "Japan",
            "location-postal_code": "",
            "location-point": '{"type":"Point","coordinates":[140.80078125000003,37.31425771585506]}',
            # ... and has been syndicated...
            "syndication-TOTAL_FORMS": "1",
            "syndication-INITIAL_FORMS": "0",
            "syndication-MIN_NUM_FORMS": "0",
            "syndication-MAX_NUM_FORMS": "1000",
            "syndication-0-url": "https://hoge.com",
            "syndication-0-id": "",
            "syndication-0-t_entry": "",
            "syndication-__prefix__-url": "",
            "syndication-__prefix__-id": "",
            "syndication-__prefix__-t_entry": "",
            # ... and is published
            "m_post_status": ["published", "published"],
            # ... for everyone to see
            "visibility": "1",
            "t_trip": "",
        }

        # Submit and...
        response = client.post(reverse("article_create"), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry = entry_models.TEntry.objects.last()
        assert entry
        assert entry.p_name == "The Week"
        assert entry.e_content == "<div>Hello</div>"
        assert entry.p_summary == "Hello"

        # ... with a post
        t_post = entry.t_post
        assert t_post
        # ... that is visible and published
        assert t_post.m_post_status.key == "published"
        assert t_post.m_post_kind.key == "article"
        assert t_post.visibility == Visibility.PUBLIC

        # ... and it is in the specified stream
        assert list(entry.t_post.streams.all()) == [stream]

        # The post has also been syndicated...
        assert entry.t_syndication.count() == 1
        syndication = entry.t_syndication.first()

        assert syndication.url == "https://hoge.com"

        # ... and a location
        location = entry.t_location

        assert location.street_address == "+"
        assert location.locality == "Kawauchi"
        assert location.region == "Fukushima+Prefecture"
        assert location.country_name == "Japan"
        assert location.postal_code == ""

        point = geos.Point((Decimal("140.80078125000003"), Decimal("37.31425771585506")))
        assert location.point.x == point.x
        assert location.point.y == point.y


@pytest.mark.django_db
class TestCreateReplyView:
    @mock.patch("application.indieweb.webmentions.ronkyuu")
    def test_creates_reply(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: A post to create a new reply entry
        Expect: A new reply to be created
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)
        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
            "m_post_kind": "article",
            "p_name": "I want to visit York",
            "e_content": "<div>Hello</div>",
            "streams": str(stream.pk),
            # Reply specific fields
            "u_in_reply_to": "https://jamesg.blog/2022/05/25/york-coffee/",
            "title": "York Coffee Recommendations",
            "summary": "I spent the weekend in York...",
            "author": "James G",
            "author_url": "",
            "author_photo_url": "",
            # ... no location
            # ... and has not been syndicated...
            "syndication-TOTAL_FORMS": "0",
            "syndication-INITIAL_FORMS": "0",
            "syndication-MIN_NUM_FORMS": "0",
            "syndication-MAX_NUM_FORMS": "1000",
            # ... and is published
            "m_post_status": ["published", "published"],
            # ... for everyone to see
            "visibility": "1",
            "t_trip": "",
        }

        # Submit and...
        response = client.post(reverse("reply_create"), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry = entry_models.TEntry.objects.last()
        assert entry
        assert entry.p_name == "I want to visit York"
        assert entry.e_content == "<div>Hello</div>"
        assert entry.p_summary == "Hello"

        # ... that should have a reply...
        reply = entry.t_reply
        assert reply.u_in_reply_to == "https://jamesg.blog/2022/05/25/york-coffee/"
        assert reply.title == "York Coffee Recommendations"
        assert reply.quote == "I spent the weekend in York..."
        assert reply.author == "James G"
        assert reply.author_url == ""
        assert reply.author_photo == ""

        # ... with a post
        t_post = entry.t_post
        assert t_post
        # ... that is visible and published
        assert t_post.m_post_status.key == "published"
        assert t_post.m_post_kind.key == "reply"
        assert t_post.visibility == Visibility.PUBLIC

        # ... and it is in the specified stream
        assert list(entry.t_post.streams.all()) == [stream]



@pytest.mark.django_db
class TestCreateBookmarkView:
    @mock.patch("application.indieweb.webmentions.ronkyuu")
    def test_creates_bookmark(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: A post to create a new bookmark entry
        Expect: A new bookmark to be created
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)
        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
            "m_post_kind": "bookmark",
            "p_name": "I want to visit York",
            "e_content": "<div>Hello</div>",
            "streams": str(stream.pk),
            # Reply specific fields
            "u_bookmark_of": "https://jamesg.blog/2022/05/25/york-coffee/",
            "title": "York Coffee Recommendations",
            "summary": "I spent the weekend in York...",
            "author": "James G",
            "author_url": "",
            "author_photo_url": "",
            # ... no location
            # ... and has not been syndicated...
            "syndication-TOTAL_FORMS": "0",
            "syndication-INITIAL_FORMS": "0",
            "syndication-MIN_NUM_FORMS": "0",
            "syndication-MAX_NUM_FORMS": "1000",
            # ... and is published
            "m_post_status": ["published", "published"],
            # ... for everyone to see
            "visibility": "1",
            "t_trip": "",
        }

        # Submit and...
        response = client.post(reverse("bookmark_create"), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry = entry_models.TEntry.objects.last()
        assert entry
        assert entry.p_name == "I want to visit York"
        assert entry.e_content == "<div>Hello</div>"
        assert entry.p_summary == "Hello"

        # ... that should have a bookmark...
        bookmark = entry.t_bookmark
        assert bookmark.u_bookmark_of == "https://jamesg.blog/2022/05/25/york-coffee/"
        assert bookmark.title == "York Coffee Recommendations"
        assert bookmark.quote == "I spent the weekend in York..."
        assert bookmark.author == "James G"
        assert bookmark.author_url == ""
        assert bookmark.author_photo == ""

        # ... with a post
        t_post = entry.t_post
        assert t_post
        # ... that is visible and published
        assert t_post.m_post_status.key == "published"
        assert t_post.m_post_kind.key == "bookmark"
        assert t_post.visibility == Visibility.PUBLIC

        # ... and it is in the specified stream
        assert list(entry.t_post.streams.all()) == [stream]
