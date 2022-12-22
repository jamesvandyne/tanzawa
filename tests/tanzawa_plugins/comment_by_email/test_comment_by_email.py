from unittest import mock

import pytest
from django.urls import reverse

from tanzawa_plugin.comment_by_email.plugin import get_plugin


@pytest.mark.django_db
class TestCommentByEmail:
    @mock.patch("application.feeds.content.plugin_pool.feed_plugins")
    def test_comment_by_email_appears_in_feed(self, feed_plugins, client, factory):
        plugin = get_plugin()

        entry = factory.StatusEntry()
        post = entry.t_post

        # Mock our feeds plugin response to force enable Comment by email.
        feed_plugins.return_value = [plugin]

        # Login as author
        client.force_login(post.p_author)
        response = client.get(reverse("public:feed"))
        feed_content = response.content.decode("utf-8")

        assert plugin.has_feed_hooks is True
        assert f"mailto:{ post.p_author.email }" in feed_content
