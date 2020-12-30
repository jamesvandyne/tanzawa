import pytest


class TestMicropub:

    @pytest.fixture
    def target(self):
        return '/micropub/'


    def test_basic_get_request(self, target, client):
        response = client.get(target)
        assert response.status_code == 200

    def test_create_entry(self, target, client):

        data = {
            "h": "entry",
            "content": "hello world",
            "action": "create",
        }
        response = client.post(target, data=data)
        assert response.status_code == 200


