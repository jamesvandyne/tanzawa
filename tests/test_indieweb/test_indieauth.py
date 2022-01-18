from unittest import mock

import pytest
from indieweb.models import TToken


@pytest.mark.django_db
class TestIndieAuthExchangeToken:
    @pytest.fixture
    def target(self):
        return "/a/indieauth/token"

    @pytest.fixture
    def post_data(self, auth_token, client_id):
        return {
            "grant_type": "authorization_code",
            "me": "https://b6260560dd45.ngrok.io/",
            "code": auth_token,
            "redirect_uri": "https://ownyourswarm.p3k.io/auth/callback",
            "client_id": client_id,
        }

    @pytest.fixture
    def ninka_mock(self, monkeypatch):
        from ninka.indieauth import discoverAuthEndpoints

        m = mock.Mock(discoverAuthEndpoints, autospec=True)
        monkeypatch.setattr("indieweb.serializers.discoverAuthEndpoints", m)
        return m

    def test_valid(self, target, client, ninka_mock, post_data, t_token):
        ninka_mock.return_value = {"redirect_uri": [post_data["redirect_uri"]]}
        response = client.post(target, data=post_data)

        assert response.status_code == 200

        data = response.json()

        assert data["me"] == post_data["me"]
        assert len(data["access_token"]) == 40
        assert data["scope"] == "create update"

        t_token.refresh_from_db()
        assert t_token.auth_token == ""
        assert t_token.key == data["access_token"]

    def test_used_token_invalid(self, target, client, ninka_mock, post_data):
        ninka_mock.return_value = {"redirect_uri": [post_data["redirect_uri"]]}
        response = client.post(target, data=post_data)
        assert response.status_code == 400
        assert response.json() == {"non_field_errors": ["Token not found"]}
        assert not ninka_mock.called

    def test_error_if_redirect_doesnt_match(self, target, client, ninka_mock, post_data, t_token):
        post_data["redirect_uri"] = "http://local.test"
        ninka_mock.return_value = {"redirect_uri": []}
        response = client.post(target, data=post_data)
        assert response.status_code == 400
        assert response.json() == {"non_field_errors": ["Redirect uri not found on client app"]}

        ninka_mock.assert_called_with(post_data["client_id"])


@pytest.mark.django_db
class TestVerifyIndieAuthToken:
    @pytest.fixture
    def target(self):
        return "/a/indieauth/token"

    def test_valid(self, target, client, t_token_access, auth_token, client_id):
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
        response = client.get(target)
        assert response.status_code == 200
        assert response.json() == {
            "me": f"/author/{t_token_access.user.username}/",
            "client_id": client_id,
            "scope": "create update",
        }

    def test_no_header(self, target, client):
        response = client.get(target)
        assert response.status_code == 400
        assert response.json() == {"message": "Invalid token header. No credentials provided."}

    def test_no_token_found(self, target, client):
        client.credentials(HTTP_AUTHORIZATION="Bearer hogehoge")
        response = client.get(target)
        assert response.status_code == 400
        assert response.json() == {"token": ["Token not found."]}


@pytest.mark.django_db
class TestIndieAuthTokenRevoke:
    @pytest.fixture
    def target(self):
        return "/a/indieauth/token"

    @pytest.fixture
    def post_data(self, auth_token, client_id):
        return {
            "action": "revoke",
            "token": auth_token,
        }

    @pytest.fixture
    def ninka_mock(self, monkeypatch):
        from ninka.indieauth import discoverAuthEndpoints

        m = mock.Mock(discoverAuthEndpoints, autospec=True)
        monkeypatch.setattr("indieweb.serializers.discoverAuthEndpoints", m)
        return m

    def test_valid(self, target, client, ninka_mock, post_data, t_token_access, auth_token):
        assert TToken.objects.filter(key=auth_token).exists() is True
        response = client.post(target, data=post_data)
        assert response.status_code == 200
        assert TToken.objects.filter(key=auth_token).exists() is False

    def test_requires_revoke(self, target, client, ninka_mock, post_data, t_token_access, auth_token):
        post_data["action"] = "hoge"
        assert TToken.objects.filter(key=auth_token).exists() is True
        response = client.post(target, data=post_data)
        assert response.status_code == 400
        assert TToken.objects.filter(key=auth_token).exists() is True


@pytest.mark.django_db
class TestIndieAuthAuthorize:
    @pytest.fixture
    def target(self):
        return "/a/indieauth/authorize"

    @pytest.fixture
    def post_data(self, auth_token, client_id):
        return {
            "response_type": "code",
            "me": "https://jamesvandyne.com",
            "redirect_uri": "https://indielogin.com/redirect/indieauth",
            "client_id": "https://indielogin.com/",
            "state": "808693bfa8c6bd1c586ea0f7",
            "code_challenge": "NJlpogsr_MNS0FVGkzF",
            "code_challenge_method": "S256",
        }

    @pytest.fixture
    def ninka_mock(self, monkeypatch):
        from ninka.indieauth import discoverAuthEndpoints

        m = mock.Mock(discoverAuthEndpoints, autospec=True)
        monkeypatch.setattr("indieweb.serializers.discoverAuthEndpoints", m)
        return m

    def test_auth_only(self, target, client, ninka_mock, user, post_data):
        """
        Confirm that the endpoint works for authorization only requests. i.e. no scope
        """
        ninka_mock.return_value = {"redirect_uri": [post_data["redirect_uri"]]}
        client.force_login(user=user)
        response = client.post(target, data=post_data)
        assert response.status_code == 302

        assert response.url == "https://indielogin.com/redirect/indieauth?state=808693bfa8c6bd1c586ea0f7"
        assert TToken.objects.count() == 0

    def test_returns_code_with_scope(self, target, client, ninka_mock, user, post_data):
        """
        Confirm that the endpoint works for authorization only requests. i.e. no scope/me
        """
        post_data["scope"] = "create"
        ninka_mock.return_value = {"redirect_uri": [post_data["redirect_uri"]]}
        client.force_login(user=user)
        response = client.post(target, data=post_data)
        assert response.status_code == 302
        t_token = TToken.objects.first()
        assert t_token is not None

        assert (
            response.url
            == f"https://indielogin.com/redirect/indieauth?state=808693bfa8c6bd1c586ea0f7&code={t_token.auth_token}"
        )
