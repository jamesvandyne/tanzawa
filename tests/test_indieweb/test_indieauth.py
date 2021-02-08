import pytest
from unittest import mock
from model_bakery import baker


@pytest.mark.django_db
class TestIndieAuthToken:

    @pytest.fixture
    def target(self):
        return '/a/indieauth/token'

    @pytest.fixture
    def auth_token(self):
        return "58a51838067faa000320f5266238d673c5897f1d"

    @pytest.fixture
    def client_id(self):
        return "https://ownyourswarm.p3k.io"

    @pytest.fixture
    def post_data(self, auth_token, client_id):
        return {
            'grant_type': 'authorization_code',
            'me': 'https://b6260560dd45.ngrok.io/',
            'code': auth_token,
            'redirect_uri': 'https://ownyourswarm.p3k.io/auth/callback',
            'client_id': client_id,
        }

    @pytest.fixture
    def ninka_mock(self, monkeypatch):
        from ninka.indieauth import discoverAuthEndpoints
        m = mock.Mock(discoverAuthEndpoints, autospec=True)
        monkeypatch.setattr('indieweb.serializers.discoverAuthEndpoints', m)
        return m

    @pytest.fixture
    def t_token(self, auth_token, client_id, m_micropub_scope):
        t_token = baker.make('indieweb.TToken',
                          auth_token=auth_token,
                          client_id=client_id
                          )
        t_token.micropub_scope.set([m_micropub_scope[0], m_micropub_scope[1]])
        return t_token

    @pytest.fixture
    def m_micropub_scope(self):
        from indieweb.models import MMicropubScope
        return MMicropubScope.objects.all()

    def test_valid(self, target, client, ninka_mock, post_data, t_token):
        ninka_mock.return_value = {"redirect_uri": [post_data['redirect_uri']]}
        response = client.post(target, data=post_data)

        assert response.status_code == 200

        data = response.json()

        assert data["me"] == post_data["me"]
        assert len(data["access_token"]) == 40
        assert data["scope"] == "create update"

        t_token.refresh_from_db()
        assert t_token.auth_token == ""
        assert t_token.access_token == data["access_token"]

    def test_used_token_invalid(self, target, client, ninka_mock, post_data):
        ninka_mock.return_value = {"redirect_uri": [post_data['redirect_uri']]}
        response = client.post(target, data=post_data)
        assert response.status_code == 400
        assert response.json() == {'non_field_errors': ['Token not found']}
        assert not ninka_mock.called

    def test_error_if_redirect_doesnt_match(self, target, client, ninka_mock, post_data, t_token):
        post_data['redirect_uri'] = 'http://local.test'
        ninka_mock.return_value = {"redirect_uri": []}
        response = client.post(target, data=post_data)
        assert response.status_code == 400
        assert response.json() == {'non_field_errors': ['Redirect uri not found on client app']}

        ninka_mock.assert_called_with(post_data['client_id'])
