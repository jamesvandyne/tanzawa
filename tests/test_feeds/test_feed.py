import pytest
from django.urls import reverse

from core.constants import Visibility


@pytest.mark.django_db
@pytest.mark.freeze_time("2020-09-28 12:59:30")
class TestFeedView:
    @pytest.fixture
    def target_url(self):
        return reverse("public:feed")

    @pytest.mark.parametrize(
        "visibility,publish_status,should_show",
        [
            (Visibility.PUBLIC, "published", True),
            (Visibility.PRIVATE, "published", True),
            (Visibility.UNLISTED, "published", False),
            # Draft Status
            (Visibility.PUBLIC, "draft", False),
            (Visibility.PRIVATE, "draft", False),
            (Visibility.UNLISTED, "draft", False),
        ],
    )
    def test_respects_visibility_for_author(
        self,
        client,
        target_url,
        factory,
        visibility,
        publish_status,
        should_show,
    ):
        if publish_status == "published":
            t_post = factory.PublishedNotePost(visibility=visibility)
        else:
            t_post = factory.DraftNotePost(visibility=visibility)
        t_entry = factory.StatusEntry(t_post=t_post)

        # Login as author
        client.force_login(t_post.p_author)
        response = client.get(target_url)
        assert should_show == (t_entry.p_summary in response.content.decode("utf-8"))

    @pytest.mark.parametrize(
        "visibility,publish_status,should_show",
        [
            (Visibility.PUBLIC, "published", True),
            (Visibility.PRIVATE, "published", False),
            (Visibility.UNLISTED, "published", False),
            # Draft Status
            (Visibility.PUBLIC, "draft", False),
            (Visibility.PRIVATE, "draft", False),
            (Visibility.UNLISTED, "draft", False),
        ],
    )
    def test_respects_visibility_another_user(
        self,
        client,
        target_url,
        factory,
        visibility,
        publish_status,
        should_show,
    ):
        if publish_status == "published":
            t_post = factory.PublishedNotePost(visibility=visibility)
        else:
            t_post = factory.DraftNotePost(visibility=visibility)
        t_entry = factory.StatusEntry(t_post=t_post)

        user = factory.User()
        client.force_login(user)
        response = client.get(target_url)
        assert should_show == (t_entry.p_summary in response.content.decode("utf-8"))

    @pytest.mark.parametrize(
        "visibility,publish_status,should_show",
        [
            (Visibility.PUBLIC, "published", True),
            (Visibility.PRIVATE, "published", False),
            (Visibility.UNLISTED, "published", False),
            (Visibility.PUBLIC, "draft", False),
            (Visibility.PRIVATE, "draft", False),
            (Visibility.UNLISTED, "draft", False),
        ],
    )
    def test_respects_visibility_for_anonymous_users(
        self,
        client,
        target_url,
        factory,
        visibility,
        publish_status,
        should_show,
    ):
        # Create an entry
        if publish_status == "published":
            t_post = factory.PublishedNotePost(visibility=visibility)
        else:
            t_post = factory.DraftNotePost(visibility=visibility)
        t_entry = factory.StatusEntry(t_post=t_post)

        response = client.get(target_url)
        assert should_show == (t_entry.p_summary in response.content.decode("utf-8"))
