import datetime
from decimal import Decimal
from unittest import mock

import pytest
from django.contrib.gis import geos
from django.urls import reverse
from django.utils import timezone

from core.constants import Visibility
from data.entry import models as entry_models
from tests import factories


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
            "tags": "coffee travel york",
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

        # ... and tags
        assert set(t_post.tags.names()) == {"coffee", "travel", "york"}


# Update


@pytest.mark.django_db
class TestUpdateStatusView:
    @mock.patch("application.indieweb.webmentions.ronkyuu")
    def test_update_status_entry_view(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: An existing entry is updated
        Expect: The status updates
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)

        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []
        published_at = timezone.localtime().now() - datetime.timedelta(days=365)
        entry = factory.StatusEntry(t_post__dt_published=published_at)

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
        response = client.post(reverse("status_edit", args=[entry.pk]), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry.refresh_from_db()
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
        # ... and the original published date remains unchanged
        assert t_post.dt_published.date() == published_at.date()

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
    def test_update_status_without_location(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: An existing status with a location
        Expect: The status can be updated and clears the location.
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)
        #
        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []

        entry = factory.StatusEntry()
        location = factory.Location(t_entry=entry)

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
        response = client.post(reverse("status_edit", args=[entry.pk]), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry.refresh_from_db()
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
            location.refresh_from_db()


@pytest.mark.django_db
class TestUpdateArticleView:
    @mock.patch("application.indieweb.webmentions.ronkyuu")
    def test_happy_path(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: An existing entry is updated
        Expect: The status updates
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)

        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []

        entry = factory.ArticleEntry()

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
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
        response = client.post(reverse("article_edit", args=[entry.pk]), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry.refresh_from_db()
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
class TestUpdateReplyView:
    @mock.patch("application.indieweb.webmentions.ronkyuu")
    def test_happy_path(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: An existing entry is updated
        Expect: The status updates
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)

        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []

        entry = factory.ReplyEntry()

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
            "summary": "Summary",
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
            "syndication-TOTAL_FORMS": "0",
            "syndication-INITIAL_FORMS": "0",
            "syndication-MIN_NUM_FORMS": "0",
            "syndication-MAX_NUM_FORMS": "1000",
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
        response = client.post(reverse("reply_edit", args=[entry.pk]), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry.refresh_from_db()
        assert entry
        assert entry.p_name == ""
        assert entry.e_content == "<div>Hello</div>"
        assert entry.p_summary == "Hello"

        # ... with a post
        t_post = entry.t_post
        assert t_post
        # ... that is visible and published
        assert t_post.m_post_status.key == "published"
        assert t_post.m_post_kind.key == "reply"
        assert t_post.visibility == Visibility.PUBLIC

        # ... and it is in the specified stream
        assert list(entry.t_post.streams.all()) == [stream]

        # ... and a reply
        reply = entry.t_reply
        assert reply.title == "Reply"
        assert reply.u_in_reply_to == "https://example.test"
        assert reply.quote == "Summary"
        assert reply.author == "John Smith"
        assert reply.author_photo == "https://example.test/jsmith/profile.png"
        assert reply.author_url == "https://example.test/jsmith"


@pytest.mark.django_db
class TestUpdateBookmarkView:
    @mock.patch("application.indieweb.webmentions.ronkyuu")
    def test_happy_path(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: An existing entry is updated
        Expect: The status updates
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)

        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []

        entry = factory.BookmarkEntry(tags=["japan"])

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
            "u_bookmark_of": "https://javahut.test",
            "title": "Javahut",
            "summary": "Summary",
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
            "syndication-TOTAL_FORMS": "0",
            "syndication-INITIAL_FORMS": "0",
            "syndication-MIN_NUM_FORMS": "0",
            "syndication-MAX_NUM_FORMS": "1000",
            "syndication-__prefix__-url": "",
            "syndication-__prefix__-id": "",
            "syndication-__prefix__-t_entry": "",
            # ... and is published
            "m_post_status": ["published", "published"],
            # ... for everyone to see
            "visibility": "1",
            "t_trip": "",
            "tags": "japan java",
        }

        # Submit and...
        response = client.post(reverse("bookmark_edit", args=[entry.pk]), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry.refresh_from_db()
        assert entry
        assert entry.p_name == ""
        assert entry.e_content == "<div>Hello</div>"
        assert entry.p_summary == "Hello"

        # ... with a post
        t_post = entry.t_post
        assert t_post
        # ... that is visible and published
        assert t_post.m_post_status.key == "published"
        assert t_post.m_post_kind.key == "bookmark"
        assert t_post.visibility == Visibility.PUBLIC

        # ... and it is in the specified stream
        assert list(entry.t_post.streams.all()) == [stream]

        # ... and tags
        assert set(t_post.tags.names()) == {"java", "japan"}

        # ... and a bookmark
        bookmark = entry.t_bookmark
        assert bookmark.title == "Javahut"
        assert bookmark.u_bookmark_of == "https://javahut.test"
        assert bookmark.quote == "Summary"
        assert bookmark.author == "John Smith"
        assert bookmark.author_photo == "https://example.test/jsmith/profile.png"
        assert bookmark.author_url == "https://example.test/jsmith"


@pytest.mark.django_db
class TestUpdateCheckinView:
    @mock.patch("application.indieweb.webmentions.ronkyuu")
    def test_happy_path(self, ronkyuu_mock, client, factory) -> None:
        """
        Given: An existing entry is updated
        Expect: The status updates
        """
        # Create a user
        admin = factory.User()
        client.force_login(admin)

        stream = factory.Stream()

        # Mock out discovering webmentions
        ronkyuu_mock.return_value = []

        entry = factory.CheckinEntry()

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
            "checkin-url": "https://javahut.test",
            "checkin-name": "Javahut",
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
        response = client.post(reverse("checkin_edit", args=[entry.pk]), payload)

        # ... redirect to the edit page
        assert response.status_code == 303

        # An entry should have been created...
        entry.refresh_from_db()
        assert entry
        assert entry.p_name == ""
        assert entry.e_content == "<div>Hello</div>"
        assert entry.p_summary == "Hello"

        # ... with a post
        t_post = entry.t_post
        assert t_post
        # ... that is visible and published
        assert t_post.m_post_status.key == "published"
        assert t_post.m_post_kind.key == "checkin"
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

        # ... and a checkin
        checkin = entry.t_checkin
        assert checkin.t_location == location
        assert checkin.name == "Javahut"
        assert checkin.url == "https://javahut.test"


@pytest.mark.django_db
class TestChangeReplyTitleView:
    def test_happy_path(self, client) -> None:
        # Create a user
        admin = factories.User()
        client.force_login(admin)

        entry = factories.ReplyEntry()
        reply = entry.t_reply

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
            "u_in_reply_to": "https://citypop.test",
            "title": "I like city pop",
        }

        # Submit and...
        response = client.post(reverse("change_reply_title", args=[entry.id]), payload)

        # ... redirect to the edit page
        assert response.status_code == 200

        # The reply should have been updated
        reply.refresh_from_db()
        assert reply.u_in_reply_to == "https://citypop.test"
        assert reply.title == "I like city pop"
        # ... and existing values that don't appear in the form shouldn't have changed.
        assert reply.quote == "Quote"
        assert reply.author == "John Smith"
        assert reply.author_photo == "https://example.test/jsmith/profile.png"
        assert reply.author_url == "https://example.test/jsmith"


@pytest.mark.django_db
class TestReplyTitle:
    def test_happy_path(self, client) -> None:
        # Create a user
        admin = factories.User()
        client.force_login(admin)

        entry = factories.ReplyEntry()
        response = client.get(reverse("reply_title", args=[entry.id]))

        # ... returns to the reply title
        assert response.status_code == 200
        assert response.context_data["title"] == entry.t_reply.title
        assert response.context_data["url"] == entry.t_reply.u_in_reply_to


@pytest.mark.django_db
class TestChangeBookmarkTitleView:
    def test_happy_path(self, client) -> None:
        # Create a user
        admin = factories.User()
        client.force_login(admin)

        entry = factories.BookmarkEntry()
        bookmark = entry.t_bookmark

        # Who submits a post
        payload = {
            "csrfmiddlewaretoken": "n59B1BvGUfxuMbCSJp5GqlZ9swSnhvanfqYmsmT4ngD86McH40tvL1nyVaGgHB7J",
            "u_bookmark_of": "https://citypop.test",
            "title": "I like city pop",
        }

        # Submit and...
        response = client.post(reverse("change_bookmark_title", args=[entry.id]), payload)

        # ... redirect to the edit page
        assert response.status_code == 200

        # The bookmark should have been updated
        bookmark.refresh_from_db()
        assert bookmark.u_bookmark_of == "https://citypop.test"
        assert bookmark.title == "I like city pop"
        # ... and existing values that don't appear in the form shouldn't have changed.
        assert bookmark.quote == "Quote"
        assert bookmark.author == "John Smith"
        assert bookmark.author_photo == "https://example.test/jsmith/profile.png"
        assert bookmark.author_url == "https://example.test/jsmith"


@pytest.mark.django_db
class TestBookmarkTitle:
    def test_happy_path(self, client) -> None:
        # Create a user
        admin = factories.User()
        client.force_login(admin)

        entry = factories.BookmarkEntry()
        response = client.get(reverse("bookmark_title", args=[entry.id]))

        # ... returns to the bookmark title
        assert response.status_code == 200
        assert response.context_data["title"] == entry.t_bookmark.title
        assert response.context_data["url"] == entry.t_bookmark.u_bookmark_of
