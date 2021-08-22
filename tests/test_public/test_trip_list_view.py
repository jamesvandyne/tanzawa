import pytest
from model_bakery import baker
from django.urls import reverse
from core.constants import Visibility


@pytest.mark.django_db
@pytest.mark.freeze_time("2020-09-28 12:59:30")
class TestTripList:
    @pytest.fixture
    def target_url(self):
        return reverse("public:trips")

    @pytest.fixture
    def author(self):
        return baker.make("auth.User", username="Author")

    @pytest.fixture
    def another_user(self):
        return baker.make("auth.User", username="Another")

    @pytest.fixture
    def t_trip(self, author, visibility):
        trip = baker.make("trips.TTrip", p_author=author, visibility=visibility, name="my trip")
        return trip

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
        self, client, target_url, t_trip, t_post, author, another_user, visibility, should_show, login_user
    ):
        if login_user:
            client.force_login(login_user)
        response = client.get(target_url)
        assert should_show == (t_trip.name in response.content.decode("utf-8"))
