import pytest
from model_bakery import baker
from indieweb.constants import MPostKinds
from core.constants import Visibility


@pytest.mark.django_db
@pytest.mark.freeze_time("2020-09-28 12:59:30")
class TestTripDetailView:
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
    def t_trip(self, t_post, author, visibility):
        trip = baker.make("trips.TTrip", p_author=author, visibility=visibility)
        baker.make("trips.TTripPost", t_trip=trip, t_post=t_post)
        return trip

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
        self, client, t_entry, t_post, t_trip, author, another_user, visibility, status_code, login_user
    ):
        if login_user:
            client.force_login(login_user)
        response = client.get(t_trip.get_absolute_url())
        assert response.status_code == status_code

    @pytest.fixture
    def public_t_trip(self, t_trip):
        t_trip.visibility = Visibility.PUBLIC
        t_trip.save()
        return t_trip

    @pytest.mark.parametrize(
        "visibility,should_show,login_user",
        [
            (Visibility.PUBLIC, True, None),
            (Visibility.PRIVATE, False, None),
            (Visibility.UNLISTED, False, None),
            (Visibility.PUBLIC, True, pytest.lazy_fixture("author")),
            (Visibility.PRIVATE, True, pytest.lazy_fixture("author")),
            (Visibility.UNLISTED, True, pytest.lazy_fixture("author")),
            (Visibility.PUBLIC, True, pytest.lazy_fixture("another_user")),
            (Visibility.PRIVATE, False, pytest.lazy_fixture("another_user")),
            (Visibility.UNLISTED, True, pytest.lazy_fixture("another_user")),
        ],
    )
    def test_respects_post_visibility(
        self, client, t_entry, t_post, public_t_trip, t_trip, author, another_user, visibility, should_show, login_user
    ):
        if login_user:
            client.force_login(login_user)
        response = client.get(public_t_trip.get_absolute_url())
        assert response.status_code == 200
        assert should_show == (t_entry.p_summary in response.content.decode("utf-8"))
