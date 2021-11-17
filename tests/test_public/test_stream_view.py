import pytest
from core.constants import Visibility
from django.urls import reverse
from indieweb.constants import MPostKinds
from model_bakery import baker


@pytest.mark.django_db
@pytest.mark.freeze_time("2020-09-28 12:59:30")
class TestStreamView:
    @pytest.fixture
    def target_url(self):
        return reverse("public:stream", args=["mine"])

    @pytest.fixture
    def m_post_kind(self, m_post_kinds):
        return m_post_kinds.get(key=MPostKinds.note)

    @pytest.fixture
    def t_post(self, t_post, author, visibility):
        m_stream = baker.make("streams.MStream", name="My Stream", slug="mine", visibility=Visibility.PUBLIC)

        t_post.p_author = author
        t_post.visibility = visibility
        t_post.save()
        t_post.streams.add(m_stream)
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
        "visibility,should_show,login_user",
        [
            (Visibility.PUBLIC, True, None),
            (Visibility.PRIVATE, False, None),
            (Visibility.UNLISTED, False, None),
            (Visibility.PUBLIC, True, pytest.lazy_fixture("author")),
            (Visibility.PRIVATE, True, pytest.lazy_fixture("author")),
            (Visibility.UNLISTED, False, pytest.lazy_fixture("author")),
            (Visibility.PUBLIC, True, pytest.lazy_fixture("another_user")),
            (Visibility.PRIVATE, False, pytest.lazy_fixture("another_user")),
            (Visibility.UNLISTED, False, pytest.lazy_fixture("another_user")),
        ],
    )
    def test_respects_visibility(
        self, client, target_url, t_entry, t_post, author, another_user, visibility, should_show, login_user
    ):
        if login_user:
            client.force_login(login_user)
        response = client.get(target_url)
        assert should_show == (t_entry.p_summary in response.content.decode("utf-8"))
