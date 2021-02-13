import pytest
from model_bakery import baker


@pytest.fixture
def auth_token():
    return "58a51838067faa000320f5266238d673c5897f1d"


@pytest.fixture
def client_id():
    return "https://ownyourswarm.p3k.io"


@pytest.fixture
def m_micropub_scope():
    from indieweb.models import MMicropubScope

    return MMicropubScope.objects.all()


@pytest.fixture
def t_token(auth_token, client_id, m_micropub_scope):
    t_token = baker.make("indieweb.TToken", auth_token=auth_token, client_id=client_id)
    t_token.micropub_scope.set([m_micropub_scope[0], m_micropub_scope[1]])
    return t_token


@pytest.fixture
def t_token_access(auth_token, client_id, m_micropub_scope):
    t_token = baker.make("indieweb.TToken", key=auth_token, client_id=client_id)
    t_token.micropub_scope.set([m_micropub_scope[0], m_micropub_scope[1]])
    return t_token
