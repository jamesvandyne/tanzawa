import pytest
from model_bakery import baker
from django.urls import reverse
from indieweb.constants import MPostKinds
from core.constants import Visibility


@pytest.mark.django_db
@pytest.mark.freeze_time("2020-09-28 12:59:30")
class TestFeedView:
    @pytest.fixture
    def target_url(self):
        return reverse("feeds:feed")

    @pytest.fixture
    def m_post_kind(self, m_post_kinds):
        return m_post_kinds.get(key=MPostKinds.note)

    @pytest.fixture
    def t_post(self, t_post, author, visibility, publish_status):
        t_post.p_author = author
        t_post.visibility = visibility
        t_post.m_post_status = publish_status
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
        "visibility,publish_status,should_show,login_user",
        [
            (Visibility.PUBLIC, pytest.lazy_fixture("published_status"), True, None),
            (Visibility.PRIVATE, pytest.lazy_fixture("published_status"), False, None),
            (Visibility.UNLISTED, pytest.lazy_fixture("published_status"), False, None),
            (Visibility.PUBLIC, pytest.lazy_fixture("published_status"), True, pytest.lazy_fixture("author")),
            (Visibility.PRIVATE, pytest.lazy_fixture("published_status"), True, pytest.lazy_fixture("author")),
            (Visibility.UNLISTED, pytest.lazy_fixture("published_status"), False, pytest.lazy_fixture("author")),
            (Visibility.PUBLIC, pytest.lazy_fixture("published_status"), True, pytest.lazy_fixture("another_user")),
            (Visibility.PRIVATE, pytest.lazy_fixture("published_status"), False, pytest.lazy_fixture("another_user")),
            (Visibility.UNLISTED, pytest.lazy_fixture("published_status"), False, pytest.lazy_fixture("another_user")),
            # Draft Status
            (Visibility.PUBLIC, pytest.lazy_fixture("draft_status"), False, None),
            (Visibility.PRIVATE, pytest.lazy_fixture("draft_status"), False, None),
            (Visibility.UNLISTED, pytest.lazy_fixture("draft_status"), False, None),
            (Visibility.PUBLIC, pytest.lazy_fixture("draft_status"), False, pytest.lazy_fixture("author")),
            (Visibility.PRIVATE, pytest.lazy_fixture("draft_status"), False, pytest.lazy_fixture("author")),
            (Visibility.UNLISTED, pytest.lazy_fixture("draft_status"), False, pytest.lazy_fixture("author")),
            (Visibility.PUBLIC, pytest.lazy_fixture("draft_status"), False, pytest.lazy_fixture("another_user")),
            (Visibility.PRIVATE, pytest.lazy_fixture("draft_status"), False, pytest.lazy_fixture("another_user")),
            (Visibility.UNLISTED, pytest.lazy_fixture("draft_status"), False, pytest.lazy_fixture("another_user")),
        ],
    )
    def test_respects_visibility(
        self,
        client,
        target_url,
        t_entry,
        t_post,
        author,
        another_user,
        visibility,
        publish_status,
        should_show,
        login_user,
    ):
        if login_user:
            client.force_login(login_user)
        response = client.get(target_url)
        assert should_show == (t_entry.p_summary in response.content.decode("utf-8"))
