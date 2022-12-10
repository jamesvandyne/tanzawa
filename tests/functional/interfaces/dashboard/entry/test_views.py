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
